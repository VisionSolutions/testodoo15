# -*- coding: utf-8 -*-

{
    "name": "Jehel Custom",
    "summary": "Jehel Custom Module",
    "version": "1.0",
    "depends": ['base', 'crm', 'sale_management', 'account', 'stock', 'mrp', 'quality_control'],
    "category": "Sales",
    "website": "https://www.envertis.in/",
    "author": "Envertis Infosoft Pvt Ltd",
    "data": [
        # 'security/ir.model.access.csv',
        'views/contact_form.xml',
        'views/sale_order.xml',
        'views/account_move.xml',
        'views/manufacturing_order.xml',
        'views/quality_control.xml',
    ],
    "application": False,
    "installable": True,
    "active": True,
}
