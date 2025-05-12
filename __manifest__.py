# -*- coding: utf-8 -*-
{
    "name": "MashiJai Shipping",
    "version": "17.0.1.0.1",
    "summary": "Peer-to-peer shipping: offer space, book shipments, and rate experiences",
    "category": "Website",
    "author": "Your Company",
    "license": "LGPL-3",
    "application": True,
    "installable": True,
    "depends": [
        "base",
        "mail",
        "website",
        "portal",
    ],
    "data": [
        # --- Sequences & Scheduled Actions ---
        "data/ir_sequence.xml",
        "data/ir_cron.xml",
        "data/shipping_cron.xml",
        # --- Settings & Mail Templates ---
        "data/res.config.xml",
        "data/mail_templates.xml",
        # --- Demo data loaded on upgrade too ---
        "demo/demo_data.xml",

        # --- Security ---
        "security/security.xml",
        "security/ir.model.access.csv",

        # --- Backend menus & views ---
        "views/menus.xml",
        "views/booking_views.xml",
        "views/booking_detail.xml",
        "views/trip_views.xml",
        "views/trip_details.xml",
        
        # --- Portal views ---
        "views/portal_my_home.xml",

        # --- Website frontend ---
        "views/create_trip_form.xml",
        "views/public_shipping_listings.xml",
        "views/search_results.xml",
        "views/my_shipping_bookings.xml",
        "views/extended_search_listings.xml",
        "views/manage_listings.xml",
        "views/website_templates.xml",

        # --- Portal integration ---
        "views/portal_buttons.xml",
        "views/portal_booking_form.xml",
        "views/portal_customer_dashboard.xml",
        "views/portal_dashboard.xml",
        "views/portal_my_bookings.xml",
        "views/portal_new_listing.xml",
        "views/portal_traveler_access.xml",
        "views/portal_traveler_dashboard.xml",

        # --- Rating snippets (if any) ---
        "views/rate_traveler.xml",
        "views/rate_user.xml",
    ],
    # we’ve removed the old demo:[] section since demo/demo_data.xml is now in data:[].
    "assets": {
        "web.assets_frontend": [
            "mashijai_shipping/static/src/js/mashijai_shipping.js",
        ],
    },
}