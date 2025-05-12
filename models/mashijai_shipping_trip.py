from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class MashiJaiShippingTrip(models.Model):
    _name = 'mashijai.shipping.trip'
    _description = 'Shipping Trip'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'departure_date desc'

    name = fields.Char(
        string='Trip Reference', required=True, copy=False, readonly=True,
        default=lambda self: _('New')
    )
    traveler_partner_id = fields.Many2one(
        'res.partner', string='Traveler', required=True
    )
    departure_city = fields.Char(required=True)
    destination_city = fields.Char(required=True)
    departure_date = fields.Date(
        required=True, tracking=True
    )
    capacity_kg = fields.Float(
        string='Total Capacity (kg)', required=True, default=100.0, tracking=True
    )
    currency_id = fields.Many2one(
        'res.currency', string='Currency',
        default=lambda self: self.env.company.currency_id.id
    )
    price = fields.Monetary(
        string='Price per kg', currency_field='currency_id', required=True
    )
    remaining_kg = fields.Float(
        string='Remaining Capacity (kg)', compute='_compute_remaining_kg', store=True
    )
    state = fields.Selection([
        ('draft', 'Draft'),
        ('open', 'Open'),
        ('fully_booked', 'Fully Booked'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
    ], default='draft', tracking=True)
    booking_ids = fields.One2many(
        'mashijai.shipping.booking', 'trip_id', string='Bookings'
    )
    
    # Fields for rating system
    traveler_rating_avg = fields.Float(
        string='Traveler Rating',
        compute='_compute_traveler_rating',
        store=False,
        help="Average rating of the traveler"
    )
    
    traveler_rating_count = fields.Integer(
        string='Traveler Rating Count',
        compute='_compute_traveler_rating',
        store=False,
        help="Number of ratings for the traveler"
    )

    def _cron_send_pre_departure_reminders(self):
        pass

    def _cron_send_post_departure_followup(self):
        pass

    def _auto_complete_trips(self):
        pass
        
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('name') or vals.get('name') == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code(
                    'mashijai.shipping.trip') or _('New')
        return super().create(vals_list)

    @api.depends('booking_ids.state', 'booking_ids.weight')
    def _compute_remaining_kg(self):
        for record in self:
            booked_weight = sum(record.booking_ids.filtered(
                lambda b: b.state in ['accepted', 'completed']
            ).mapped('weight'))
            record.remaining_kg = record.capacity_kg - booked_weight

    @api.depends('traveler_partner_id')
    def _compute_traveler_rating(self):
        """Compute the average rating and count for a traveler"""
        for record in self:
            domain = [
                ('res_model', '=', 'mashijai.shipping.booking'),
                ('rated_partner_id', '=', record.traveler_partner_id.id),
                ('rating', '!=', False),
                ('consumed', '=', True)
            ]
            ratings = self.env['rating.rating'].search(domain)
            
            record.traveler_rating_count = len(ratings)
            record.traveler_rating_avg = sum(r.rating for r in ratings) / len(ratings) if ratings else 0.0

    @api.constrains('departure_date')
    def _check_departure_date(self):
        for rec in self:
            if rec.departure_date < fields.Date.today():
                raise ValidationError(
                    _('Departure date cannot be in the past.')
                )

    @api.constrains('capacity_kg')
    def _check_capacity_positive(self):
        for rec in self:
            if rec.capacity_kg <= 0:
                raise ValidationError(
                    _('Total capacity must be greater than zero.')
                )

    @api.constrains('price')
    def _check_price_positive(self):
        for rec in self:
            if rec.price <= 0:
                raise ValidationError(
                    _('Price must be greater than zero.')
                )

    def action_confirm(self):
        for record in self:
            if record.state == 'draft':
                record.state = 'open'

    def action_cancel(self):
        for record in self:
            if record.state not in ['completed', 'cancelled']:
                record.state = 'cancelled'
                
    def action_complete(self):
        """Mark trip as completed"""
        for record in self:
            if record.state not in ['completed', 'cancelled']:
                record.state = 'completed'
                
    def _update_trip_state(self):
        """Update trip state based on bookings"""
        self.ensure_one()
        if self.state in ['open', 'fully_booked']:
            if self.remaining_kg <= 0:
                self.state = 'fully_booked'
            else:
                self.state = 'open'
                
    def get_traveler_ratings(self, limit=5):
        """Get recent ratings for this traveler"""
        self.ensure_one()
        domain = [
            ('res_model', '=', 'mashijai.shipping.booking'),
            ('rated_partner_id', '=', self.traveler_partner_id.id),
            ('rating', '!=', False),
            ('consumed', '=', True)
        ]
        return self.env['rating.rating'].search(domain, order='create_date desc', limit=limit)