# MashiJai Shipping - Odoo 17 Module

## Overview

MashiJai Shipping is a peer-to-peer shipping platform developed by webTronex that connects travelers with excess luggage space to customers needing to ship items along the same route. This module integrates with the Odoo portal to provide a seamless experience for both travelers and customers.
https://www.webTronex.a
support@webTronex.ca

## Key Features

- **Trip Management**: Create and manage shipping trips with origin, destination, dates, and capacity
- **Booking System**: Request, approve, and complete bookings between travelers and customers
- **Portal Integration**: Full portal access for travelers and customers
- **Public Search**: Search available shipping options without logging in
- **Rating System**: Rate and review travelers based on shipping experiences

## Installation

```bash
# Install the module (via UI or command line)
odoo -d yourdatabase -i mashijai_shipping
```

## Usage

### For Travelers

1. Join as a traveler by requesting traveler access
2. Create trips with available capacity
3. Accept or reject booking requests
4. Complete bookings when delivery is made
5. Build a positive reputation through customer ratings

### For Customers

1. Search available shipping options
2. Book available space
3. Track booking status
4. Complete the booking once delivery is received
5. Rate your experience with the traveler

## Rating System

The module includes a comprehensive rating system that allows:

- Automatic rating requests after booking completion
- 1-5 star ratings with optional feedback
- Rating reminders for incomplete ratings
- Display of average ratings in trip listings
- Traveler rating statistics in profiles

## Upgrade Notes

### Upgrading from v1.0.0 to v1.0.1

This version adds the rating system and fixes portal sidebar integration for Odoo 17. To upgrade:

```bash
# Pull the latest code
cd /path/to/odoo/addons/mashijai_shipping
git pull

# Upgrade the module
odoo -d yourdatabase -u mashijai_shipping
```

The migration process will:
- Add necessary fields for rating functionality
- Create initial rating records for previously completed bookings
- Fix portal sidebar integration

## Troubleshooting

### Common Issues

1. **500 Error on Portal Pages**:
   - Clear browser cache
   - Restart Odoo with `--update=mashijai_shipping`

2. **Rating Stars Not Appearing**:
   - Check browser console for JavaScript errors
   - Ensure rating widget JS is loaded (check Assets debugging)

3. **Email Templates Not Sending**:
   - Verify outgoing email configuration in Odoo
   - Check email templates in Settings → Technical → Email Templates

## Contributing

Contributions to the MashiJai Shipping module are welcome. Please follow these steps:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

LGPL-3
