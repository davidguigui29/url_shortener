# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
from urllib.parse import urlparse

class URLRedirectController(http.Controller):

    @http.route(['/s/<string:short_code>'], type='http', auth="public", website=True)
    def redirect_short_url(self, short_code, **kw):
        short_url = request.env['short.url'].sudo().search([('short_code', '=', short_code)], limit=1)
        if not short_url:
            return request.render('website.404')

        target = short_url.original_url.strip()

        # ✅ Ensure full absolute URL format
        if not target.lower().startswith(('http://', 'https://')):
            target = 'https://' + target

        # ✅ Sanity check: must have a domain part
        parsed = urlparse(target)
        if not parsed.netloc:
            return request.render('website.404')

        # ✅ Increment click count
        short_url.sudo().write({'click_count': short_url.click_count + 1})

        # ✅ Explicitly use werkzeug redirect to avoid Odoo rewriting
        from werkzeug.utils import redirect
        response = redirect(target, code=302)
        response.autocorrect_location_header = False  # prevents domain rewriting
        return response
