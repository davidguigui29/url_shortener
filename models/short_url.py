# -*- coding: utf-8 -*-
import string
import random
import re
from urllib.parse import urlparse
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

_HOSTNAME_TLD_RE = re.compile(r'^[A-Za-z0-9-]+(\.[A-Za-z0-9-]+)*\.[A-Za-z]{2,}$')
_IPV4_RE = re.compile(r'^\d{1,3}(\.\d{1,3}){3}$')


class ShortURL(models.Model):
    _name = 'short.url'
    _description = 'Shortened URL'
    _rec_name = 'short_code'

    name = fields.Char(string='Title')
    original_url = fields.Char(string='Original URL', required=True)
    short_code = fields.Char(string='Short Code', copy=False, index=True, readonly=True)
    short_url = fields.Char(string='Short URL', compute='_compute_short_url', store=True)
    click_count = fields.Integer(string='Clicks', default=0)

    @api.depends('short_code')
    def _compute_short_url(self):
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        for rec in self:
            rec.short_url = f"{base_url}/s/{rec.short_code}" if rec.short_code else False

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('short_code'):
                vals['short_code'] = self._generate_short_code()

            url = vals.get('original_url', '').strip()
            if url and not url.lower().startswith(('http://', 'https://')):
                url = 'https://' + url
            # normalize
            vals['original_url'] = url
            # validate
            self._validate_url(url)
        return super().create(vals_list)

    def write(self, vals):
        if 'original_url' in vals:
            url = vals['original_url'].strip()
            if url and not url.lower().startswith(('http://', 'https://')):
                url = 'https://' + url
            vals['original_url'] = url
            self._validate_url(url)
        return super().write(vals)

    def _generate_short_code(self, length=6):
        """Generate unique alphanumeric short code"""
        chars = string.ascii_letters + string.digits
        while True:
            code = ''.join(random.choice(chars) for _ in range(length))
            if not self.search([('short_code', '=', code)], limit=1):
                return code

    def _validate_url(self, url):
        """Ensure the URL is an absolute HTTP(S) URL and hostname looks valid."""
        if not url:
            raise ValidationError(_("Original URL cannot be empty."))

        parsed = urlparse(url)
        scheme = (parsed.scheme or '').lower()
        hostname = parsed.hostname or ''

        # must be http(s)
        if scheme not in ('http', 'https'):
            raise ValidationError(_("URL must start with http:// or https://"))

        # hostname must exist
        if not hostname:
            raise ValidationError(_("Invalid URL: missing hostname."))

        # allow localhost
        if hostname == 'localhost':
            return True

        # allow IPv4
        if _IPV4_RE.match(hostname):
            # basic numeric range check (0-255) for each octet
            parts = hostname.split('.')
            valid = all(0 <= int(p) <= 255 for p in parts)
            if not valid:
                raise ValidationError(_("Invalid IPv4 address in URL."))
            return True

        # require hostname with a dot + TLD (e.g. example.com)
        if not _HOSTNAME_TLD_RE.match(hostname):
            raise ValidationError(_("Invalid hostname. Please include a valid domain (e.g. example.com)."))

        return True

    @api.onchange('original_url')
    def _onchange_original_url(self):
        """Onchange: normalize and warn user if format is suspicious."""
        if not self.original_url:
            return

        url = self.original_url.strip()
        if not url.lower().startswith(('http://', 'https://')):
            url = 'https://' + url
        # quick parse for immediate feedback
        parsed = urlparse(url)
        hostname = parsed.hostname or ''

        # prepare warning if hostname doesn't look like a proper domain
        if hostname and hostname not in ('localhost',) and not (_IPV4_RE.match(hostname) or _HOSTNAME_TLD_RE.match(hostname)):
            return {
                'warning': {
                    'title': _('Suspicious URL format'),
                    'message': _('The hostname "%s" does not look like a valid domain. Please include a full domain (e.g. example.com) or a valid IP.') % hostname
                }
            }




# # -*- coding: utf-8 -*-
# import string
# import random
# from urllib.parse import urlparse
# from odoo import models, fields, api, _
# from odoo.exceptions import ValidationError


# class ShortURL(models.Model):
#     _name = 'short.url'
#     _description = 'Shortened URL'
#     _rec_name = 'short_code'

#     name = fields.Char(string='Title')
#     original_url = fields.Char(string='Original URL', required=True)
#     short_code = fields.Char(string='Short Code', copy=False, index=True, readonly=True)
#     short_url = fields.Char(string='Short URL', compute='_compute_short_url', store=True)
#     click_count = fields.Integer(string='Clicks', default=0)

#     @api.depends('short_code')
#     def _compute_short_url(self):
#         base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
#         for rec in self:
#             rec.short_url = f"{base_url}/s/{rec.short_code}" if rec.short_code else False

#     @api.model_create_multi
#     def create(self, vals_list):
#         for vals in vals_list:
#             # Ensure a short code exists
#             if not vals.get('short_code'):
#                 vals['short_code'] = self._generate_short_code()

#             # Clean and validate the URL
#             url = vals.get('original_url', '').strip()
#             if url and not url.lower().startswith(('http://', 'https://')):
#                 url = 'https://' + url
#             self._validate_url(url)
#             vals['original_url'] = url
#         return super().create(vals_list)

#     def write(self, vals):
#         if 'original_url' in vals:
#             url = vals['original_url'].strip()
#             if url and not url.lower().startswith(('http://', 'https://')):
#                 url = 'https://' + url
#             self._validate_url(url)
#             vals['original_url'] = url
#         return super().write(vals)

#     def _generate_short_code(self, length=6):
#         """Generate unique alphanumeric short code"""
#         chars = string.ascii_letters + string.digits
#         while True:
#             code = ''.join(random.choice(chars) for _ in range(length))
#             if not self.search([('short_code', '=', code)], limit=1):
#                 return code

#     def _validate_url(self, url):
#         """Ensure the given URL is valid and uses HTTP(S)."""
#         parsed = urlparse(url)
#         if not parsed.scheme or not parsed.netloc:
#             raise ValidationError(_("Invalid URL format. Please enter a valid URL, e.g., https://example.com"))

