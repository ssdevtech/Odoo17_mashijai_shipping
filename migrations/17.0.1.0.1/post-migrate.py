from odoo import api, SUPERUSER_ID
from odoo.tools.sql import column_exists

def migrate(cr, version):
    """
    Post-migration script for version 17.0.1.0.1.
    - Adds rating_requested field to existing completed bookings
    - Creates any missing rating records for completed bookings
    """
    if not version:
        return
        
    env = api.Environment(cr, SUPERUSER_ID, {})
    
    # 1. Check if completed bookings have the rating_requested field
    if not column_exists(cr, 'mashijai_shipping_booking', 'rating_requested'):
        cr.execute("""
            ALTER TABLE mashijai_shipping_booking
            ADD COLUMN rating_requested boolean DEFAULT FALSE
        """)
    
    # 2. Mark all completed bookings as having rating requested
    cr.execute("""
        UPDATE mashijai_shipping_booking
        SET rating_requested = TRUE
        WHERE state = 'completed'
    """)
    
    # 3. Ensure all completed bookings have a rating record
    BookingModel = env['mashijai.shipping.booking']
    RatingModel = env['rating.rating']
    
    # Get all completed bookings
    completed_bookings = BookingModel.search([('state', '=', 'completed')])
    
    for booking in completed_bookings:
        # Check if a rating record already exists
        existing_rating = RatingModel.search([
            ('res_model', '=', 'mashijai.shipping.booking'),
            ('res_id', '=', booking.id),
            ('partner_id', '=', booking.requester_id.id),
        ], limit=1)
        
        if not existing_rating:
            # Create a new rating record
            RatingModel.create({
                'res_model_id': env['ir.model']._get('mashijai.shipping.booking').id,
                'res_id': booking.id,
                'partner_id': booking.requester_id.id,
                'rated_partner_id': booking.trip_id.traveler_partner_id.id,
                'rating': 0,
                'consumed': False,
            })
    
    # 4. Compute booking_reference for all ratings
    ratings = RatingModel.search([
        ('res_model', '=', 'mashijai.shipping.booking'),
        ('booking_reference', '=', False)
    ])
    if ratings:
        ratings._compute_booking_reference()