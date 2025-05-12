# -*- coding: utf-8 -*-
import logging
from odoo import http, _
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal

_logger = logging.getLogger(__name__)

class MashiJaiShippingPortal(CustomerPortal):
    """Portal controller for MashiJai Shipping"""

    @http.route(['/my', '/my/home'], type='http', auth="user", website=True)
    def portal_my_home(self, **kw):
        counters = self._get_page_counters()
        counters.extend(['shipping_count', 'trip_count'])
        values = self._prepare_home_portal_values(counters)
        return request.render('portal.portal_my_home', values)

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        partner = request.env.user.partner_id
        if 'shipping_count' in counters:
            values.update({
                'shipping_count': request.env['mashijai.shipping.booking'].sudo().search_count([
                    ('requester_id', '=', partner.id)
                ]),
                'trip_count': request.env['mashijai.shipping.trip'].sudo().search_count([
                    ('traveler_partner_id', '=', partner.id)
                ])
            })
        return values

    def _prepare_portal_layout_values(self):
        values = super()._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        values.update({
            'shipping_count': request.env['mashijai.shipping.booking'].sudo().search_count([
                ('requester_id', '=', partner.id)
            ]),
            'trip_count': request.env['mashijai.shipping.trip'].sudo().search_count([
                ('traveler_partner_id', '=', partner.id)
            ]),
            'is_traveler': request.env.user.has_group('mashijai_shipping.group_mashijai_traveler'),
            'trip': request.env['mashijai.shipping.trip'],  # safe default
        })
        return values

    @http.route('/', type='http', auth='public', website=True)
    def index(self, **kw):
        trips = request.env['mashijai.shipping.trip'].sudo().search(
            [('state', '=', 'open'), ('remaining_kg', '>', 0)],
            limit=6, order='departure_date asc')
        return request.render('website.homepage', {
            'trips': trips,
            'user_id': request.env.user,
            'search_params': {},
        })

    @http.route('/shipping/search', type='http', auth='public', website=True)
    def search_trips(self, **kw):
        domain = [('state', '=', 'open'), ('remaining_kg', '>', 0)]
        if kw.get('departure_city'):
            domain.append(('departure_city', 'ilike', kw['departure_city']))
        if kw.get('destination_city'):
            domain.append(('destination_city', 'ilike', kw['destination_city']))
        if kw.get('date_from'):
            domain.append(('departure_date', '>=', kw['date_from']))
        if kw.get('date_to'):
            domain.append(('departure_date', '<=', kw['date_to']))

        trips = request.env['mashijai.shipping.trip'].sudo().search(
            domain, order='departure_date asc')
        return request.render('mashijai_shipping.search_results', {
            'trips': trips,
            'search_params': kw,
            'error': False,
            'user_id': request.env.user,
        })

    @http.route(['/my/shipping/dashboard'], type='http', auth='user', website=True)
    def shipping_dashboard(self, **kw):
        try:
            values = self._prepare_portal_layout_values()
            partner = request.env.user.partner_id
            trips = request.env['mashijai.shipping.trip'].sudo().search(
                [('traveler_partner_id', '=', partner.id)], order='departure_date desc')
            bookings = request.env['mashijai.shipping.booking'].sudo().search(
                [('requester_id', '=', partner.id)], order='create_date desc')
            values.update({
                'page_name': 'shipping_dashboard',
                'trips': trips,
                'bookings': bookings
            })
            return request.render('mashijai_shipping.portal_shipping_dashboard', values)
        except Exception as e:
            _logger.error("Dashboard error: %s", e)
            return request.redirect('/my')

    @http.route(['/my/shipping/trips/create'], type='http', auth='user', website=True, methods=['GET', 'POST'])
    def create_trip(self, **post):
        if not request.env.user.has_group('mashijai_shipping.group_mashijai_traveler'):
            return request.render('mashijai_shipping.portal_traveler_access')
        if request.httprequest.method == 'POST':
            vals = {
                'traveler_partner_id': request.env.user.partner_id.id,
                'departure_city': post.get('departure_city'),
                'destination_city': post.get('destination_city'),
                'departure_date': post.get('departure_date'),
                'capacity_kg': float(post.get('capacity_kg', 0)),
                'price': float(post.get('price', 0)),
                'state': 'open',
            }
            try:
                request.env['mashijai.shipping.trip'].sudo().create(vals)
                return request.redirect('/my/shipping/dashboard')
            except Exception as e:
                _logger.error("Trip creation error: %s", e)
                values = self._prepare_portal_layout_values()
                values.update({'error_message': str(e), 'post': post})
                return request.render('mashijai_shipping.create_trip_form', values)
        return request.render('mashijai_shipping.create_trip_form', self._prepare_portal_layout_values())

    @http.route('/my/shipping/trip/<int:trip_id>/requests', type='http', auth='user', website=True)
    def trip_requests(self, trip_id, **kw):
        values = self._prepare_portal_layout_values()
        trip = request.env['mashijai.shipping.trip'].sudo().browse(trip_id)
        bookings = request.env['mashijai.shipping.booking'].sudo().search([('trip_id', '=', trip_id)])
        values.update({'page_name': 'manage_listings', 'trip': trip, 'bookings': bookings})
        return request.render('mashijai_shipping.manage_listings', values)

    @http.route('/my/shipping/book/<int:trip_id>', type='http', auth='user', website=True)
    def book_trip(self, trip_id, **kw):
        values = self._prepare_portal_layout_values()
        trip = request.env['mashijai.shipping.trip'].sudo().browse(trip_id)
        values.update({'trip': trip})
        return request.render('mashijai_shipping.portal_booking_form', values)

    @http.route('/my/shipping/bookings', type='http', auth='user', website=True)
    def my_bookings(self, **kw):
        values = self._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        bookings = request.env['mashijai.shipping.booking'].sudo().search(
            [('requester_id', '=', partner.id)], order='create_date desc')
        values.update({'page_name': 'my_bookings', 'bookings': bookings})
        return request.render('mashijai_shipping.portal_my_bookings', values)

    @http.route('/my/shipping/rate_user', type='http', auth='user', website=True)
    def rate_user(self, **kw):
        return request.render('mashijai_shipping.rate_user', self._prepare_portal_layout_values())

    @http.route('/my/shipping/rate_traveler', type='http', auth='user', website=True)
    def rate_traveler(self, **kw):
        return request.render('mashijai_shipping.rate_traveler', self._prepare_portal_layout_values())

    @http.route(['/discuss/redirect'], type='http', auth='user', website=True)
    def discuss_redirect(self, **kw):
        return request.redirect('/web#action=mail.action_discuss')