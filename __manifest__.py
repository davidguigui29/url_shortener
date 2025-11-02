# -*- coding: utf-8 -*-
{
    'name': 'URL Shortener',
    'version': '1.0',
    'category': 'Tools',
    'summary': 'Shorten long URLs using your own domain (guidasworld.com)',
    'author': 'Guidasworld',
    'website': 'https://guidasworld.com',
    'depends': ['base', 'website'],
    'data': [
        'security/ir.model.access.csv',
        'data/short_url_sequence.xml',
        'views/short_url_views.xml',
    ],


    'application': True,
    'license': 'LGPL-3',
}
