# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import datetime
from odoo import api, fields, models, _


class SaleOrder(models.Model):
    _inherit = "sale.order"

    transporter_name = fields.Char("Transporter Name")
    lr_no = fields.Char("LR No.")
    warranty = fields.Selection([
        ('18_months_of_date_of_commission', '18 months of date of commission'),
        ('36_months_from_the_date_of_delivery', '36 months from the date of delivery'),
        ('12_months_from_date_of_erection_&_commissioning', '12 months from date of erection & commissioning')
    ], 'Warranty ', default='18_months_of_date_of_commission')
    # expected_delivery_date = fields.Datetime("Expected Delivery Date")
    # delivery_date = fields.Datetime("Delivery Date")
    transport = fields.Selection([
        ('ex', 'Ex-Works'),
        ('included', 'FOR site')
    ], string='Transport', default='ex')

    def _prepare_invoice(self):
        invoice_vals = super(SaleOrder, self)._prepare_invoice()
        invoice_vals['transporter_name'] = self.transporter_name or ''
        invoice_vals['lr_no'] = self.lr_no or ''
        return invoice_vals
