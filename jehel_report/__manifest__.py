# -*- coding: utf-8 -*-

{
    "name": "Jehel Report",
    "summary": "Jehel Report Module",
    "version": "1.0",
    "depends": ['base', 'sale_stock','mrp', 'sale_management', 'purchase'],
    "category": "Sales",
    "website": "https://www.envertis.in/",
    "author": "Envertis Infosoft Pvt Ltd",
    "data": [
        'views/res_company.xml',
        'report/purchase_report.xml',
        'report/sale_report.xml',
        'report/proforma_invoice_report.xml',
        'report/invoice_report.xml',
        'report/mrp_report.xml',
        'data/mail_template.xml',
    ],
    "application": False,
    "installable": True,
    "active": True,
}
