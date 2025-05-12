# -*- coding: utf-8 -*-
import logging
from odoo import http
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal

_logger = logging.getLogger(__name__)

class MashiJaiShippingPortal(CustomerPortal):

    @http.route(['/my/shipping/traveler'], type='http', auth="user", website=True)
    def portal_traveler_dashboard(self, **kw):
        values = self._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        trips = request.env['mashijai.shipping.trip'].sudo().search([
            ('traveler_partner_id', '=', partner.id)
        ], order='departure_date desc')
        values.update({
            'page_name': 'traveler_dashboard',
            'trips': trips,
        })
        return request.render('mashijai_shipping.portal_traveler_dashboard', values)

    @http.route(['/my/shipping/customer'], type='http', auth="user", website=True)
    def portal_customer_dashboard(self, **kw):
        values = self._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        bookings = request.env['mashijai.shipping.booking'].sudo().search([
            ('requester_id', '=', partner.id)
        ], order='create_date desc')
        values.update({
            'page_name': 'customer_dashboard',
            'bookings': bookings,
        })
        return request.render('mashijai_shipping.portal_customer_dashboard', values)