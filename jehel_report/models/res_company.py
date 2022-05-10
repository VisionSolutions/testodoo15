# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, tools, _
from functools import partial
from odoo.tools import formatLang
import math
from num2words import num2words
import logging


class Company(models.Model):
    _inherit = 'res.company'

    cin_no = fields.Char("CIN No.")
    iec_no = fields.Char("IEC No.")
    reg_office = fields.Text("Regd.Office")


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    vendor_ref_date = fields.Datetime("Customer Reference Date")
    # terms and condition
    p_f = fields.Text("PACKING & FORWARDING")
    s_price = fields.Char("Price Basis")
    gst = fields.Char("GST")
    freight = fields.Text("Freight")
    t_i = fields.Text("Transit & Insurance")
    deliver = fields.Text("DELIVERY")
    s_warranty = fields.Text("Test/Warranty/Guarantee Certificate")
    payment_terms = fields.Text("Payment Terms")


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    pi_no = fields.Char("P.I. No.")
    client_order_ref_date = fields.Datetime("Customer Reference Date")
    # terms and condition
    s_price = fields.Char("PRICE")
    p_f = fields.Text("PACKING & FORWARDING")
    t_d = fields.Text("TAXES & DUTIES")
    deliver = fields.Text("DELIVERY")
    t_p = fields.Text("TERMS OF PAYMENT")
    t_i = fields.Text("TRANSPORTATION & INSURANCE")
    s_e_c = fields.Text("SUPERVISION OF ERECTION & COMMISSIONING")
    s_warranty = fields.Text("WARRANTY")
    f_m_c = fields.Text("FORCE MAJEURE CLAUSE")
    o_v = fields.Text("OFFER VALIDITY")
    k_p_r_o_v = fields.Text("KEY POINTS REGARDING ORDER VALIDITY")


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    rounding = fields.Float(string='Rounding Factor', digits=(12, 6), default=0.01,
        help='Amounts in this currency are rounded off to the nearest multiple of the rounding factor.')
    decimal_places = fields.Integer(compute='_compute_decimal_places', store=True,
        help='Decimal places taken into account for operations on amounts in this currency. It is determined by the rounding factor.')

    @api.depends('rounding')
    def _compute_decimal_places(self):
        for currency in self:
            if 0 < currency.rounding < 1:
                currency.decimal_places = int(math.ceil(math.log10(1/currency.rounding)))
            else:
                currency.decimal_places = 0

    def is_zero(self, amount):
        self.ensure_one()
        return tools.float_is_zero(amount, precision_rounding=self.rounding)

    def amount_to_text_qty(self, amount):
        self.ensure_one()
        def _num2words(number, lang):
            try:
                return num2words(number, lang=lang).title()
            except NotImplementedError:
                return num2words(number, lang='en').title()

        if num2words is None:
            logging.getLogger(__name__).warning("The library 'num2words' is missing, cannot render textual amounts.")
            return ""

        formatted = "%.{0}f".format(self.decimal_places) % amount
        parts = formatted.partition('.')
        integer_value = int(parts[0])
        fractional_value = int(parts[2] or 0)

        lang = tools.get_lang(self.env)
        amount_words = tools.ustr('{amt_value}').format(
                        amt_value=_num2words(integer_value, lang=lang.iso_code),
                        # amt_word=self.currency_unit_label,
                        )
        if not self.is_zero(amount - integer_value):
            amount_words += ' ' + _('and') + tools.ustr(' {amt_value} ').format(
                        amt_value=_num2words(fractional_value, lang=lang.iso_code),
                        # amt_word=self.currency_subunit_label,
                        )
        return amount_words


class AccountMove(models.Model):
    _inherit = 'account.move'

    pck_list_way_bill_attch = fields.Char("Packing List & Way Bill Attached")
    vehicle_no = fields.Char("Vehicle No")
    waybill_no = fields.Char("Waybill No")
    invoice_ref_date = fields.Datetime("Invoice Refence Date")


class MrpProductionInherit(models.Model):
    _inherit = 'mrp.production'

    sale_order_id = fields.Many2one('sale.order', 'Sales Order')

    @api.model
    def create(self, vals):
        rec = super(MrpProductionInherit, self).create(vals)
        if 'origin' in vals and vals.get('origin', False):
            origin = vals.get('origin', '').split(' - ')[-1]
            order = self.env['sale.order'].sudo().search([('name', '=', origin)], limit=1)
            if not order:
                context = self._context.get('params', {})
                sale = context.get('origins', {False: False})
                origin = list(sale)[-1]
                if origin:
                    order = self.env['sale.order'].sudo().search([('name', '=', origin)], limit=1)
            rec.sale_order_id = order.id
        return rec
