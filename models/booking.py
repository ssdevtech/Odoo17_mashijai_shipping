from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class MashiJaiShippingBooking(models.Model):
    _name = 'mashijai.shipping.booking'
    _description = 'Shipping Booking'
    _inherit = ['mail.thread', 'mail.activity.mixin']  # Removed rating.mixin temporarily
    _order = 'create_date desc'

    def _get_mail_thread_data(self, request_list):
        """Required method for mail integration"""
        res = {}
        for thread in self:
            res[thread.id] = {
                'hasWriteAccess': thread.with_user(self.env.user).check_access_rights('write', raise_exception=False),
                'hasReadAccess': thread.with_user(self.env.user).check_access_rights('read', raise_exception=False),
                'isFollowing': thread.message_is_follower,
                'followerCount': len(thread.message_follower_ids),
            }
        return res

    name = fields.Char(
        string='Booking Reference',
        required=True,
        copy=False,
        readonly=True,
        default=lambda self: _('New')
    )
    
    trip_id = fields.Many2one(
        'mashijai.shipping.trip',
        string='Trip',
        required=True,
        ondelete='cascade',
        tracking=True
    )
    
    requester_id = fields.Many2one(
        'res.partner',
        string='Requester',
        required=True,
        tracking=True
    )
    
    weight = fields.Float(
        string='Weight (kg)',
        required=True,
        tracking=True
    )
    
    description = fields.Text(
        string='Booking Description',
        tracking=True
    )
    
    currency_id = fields.Many2one(
        related='trip_id.currency_id',
        store=True
    )
    
    unit_price = fields.Monetary(
        related='trip_id.price',
        string='Price per kg',
        currency_field='currency_id',
        store=True
    )
    
    total_price = fields.Monetary(
        string='Total Price',
        compute='_compute_total_price',
        currency_field='currency_id',
        store=True,
        tracking=True
    )
    
    state = fields.Selection([
        ('draft', 'Draft'),
        ('pending', 'Pending Approval'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
    ], default='draft', tracking=True)

    # Basic field for completion date without rating functionality
    completion_date = fields.Datetime(
        string='Completion Date',
        readonly=True
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('mashijai.shipping.booking') or _('New')
        return super().create(vals_list)

    @api.depends('weight', 'unit_price')
    def _compute_total_price(self):
        for record in self:
            record.total_price = record.weight * record.unit_price

    @api.constrains('weight', 'trip_id')
    def _check_weight(self):
        for record in self:
            if record.weight <= 0:
                raise ValidationError(_('Weight must be greater than 0'))
            if record.weight > record.trip_id.remaining_kg:
                raise ValidationError(_(
                    'Requested weight (%.2f kg) exceeds available capacity (%.2f kg)'
                ) % (record.weight, record.trip_id.remaining_kg))

    def action_submit(self):
        """Submit booking for approval"""
        for record in self:
            if record.state == 'draft':
                record.state = 'pending'
                record._notify_trip_owner()
                msg = _("Booking submitted for approval")
                record.message_post(body=msg, message_type='notification')

    def action_accept(self):
        """Accept the booking"""
        for record in self:
            if record.state == 'pending':
                record.state = 'accepted'
                record.trip_id._update_trip_state()
                record._notify_requester('accepted')
                msg = _("Booking accepted")
                record.message_post(body=msg, message_type='notification')

    def action_reject(self):
        """Reject the booking"""
        for record in self:
            if record.state == 'pending':
                record.state = 'rejected'
                record._notify_requester('rejected')
                msg = _("Booking rejected")
                record.message_post(body=msg, message_type='notification')

    def action_cancel(self):
        """Cancel the booking"""
        for record in self:
            if record.state in ['draft', 'pending']:
                record.state = 'cancelled'
                record.trip_id._update_trip_state()
                msg = _("Booking cancelled")
                record.message_post(body=msg, message_type='notification')
    
    def action_complete(self):
        """Mark booking as completed"""
        for record in self:
            if record.state == 'accepted':
                record.write({
                    'state': 'completed',
                    'completion_date': fields.Datetime.now()
                })
                record.trip_id._update_trip_state()
                
                msg = _("Booking completed")
                record.message_post(body=msg, message_type='notification')
                
        return True

    def _notify_trip_owner(self):
        """Send notification to trip owner"""
        self.ensure_one()
        template = self.env.ref('mashijai_shipping.email_template_new_booking', False)
        if template:
            template.send_mail(self.id, force_send=True)

    def _notify_requester(self, action):
        """Send notification to requester"""
        self.ensure_one()
        template_xml_id = (
            'mashijai_shipping.email_template_booking_accepted'
            if action == 'accepted'
            else 'mashijai_shipping.email_template_booking_rejected'
        )
        template = self.env.ref(template_xml_id, False)
        if template:
            template.send_mail(self.id, force_send=True)