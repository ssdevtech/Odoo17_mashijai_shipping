from odoo import models, fields, api

class RatingInherit(models.Model):
    _inherit = 'rating.rating'

    booking_reference = fields.Char(string='Booking Reference', compute='_compute_booking_reference', store=True)

    @api.depends('res_model', 'res_id')
    def _compute_booking_reference(self):
        for record in self:
            if record.res_model == 'mashijai.shipping.booking':
                booking = self.env['mashijai.shipping.booking'].browse(record.res_id)
                if booking.exists():
                    record.booking_reference = booking.name
                else:
                    record.booking_reference = False
            else:
                record.booking_reference = False