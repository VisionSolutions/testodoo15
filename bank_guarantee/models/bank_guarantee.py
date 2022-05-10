# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

from babel.dates import format_datetime, format_date


class BankGuarantee(models.Model):
    _name = 'bank.guarantee'
    _description = "Bank Guarantee"
    _rec_name = 'name'

    sequence = fields.Integer(default=10)
    name = fields.Char("Bank Name")
    bank_type = fields.Selection([
        ('advance_bank_guarantee', 'Advance Bank Guarantee'),
        ('performance_bank_guarantee', 'Performance Bank Guarantee')
    ], 'Type', default='advance_bank_guarantee')
    reference_no = fields.Char(string="Reference No.")
    our_sale_order_no = fields.Many2one("sale.order", "Our Sale Order No")
    # customer_name = fields.Char("Customers Name")
    partner_id = fields.Many2one("res.partner", "Customers Name")
    cust_po_no = fields.Char("Customer PO No.")
    sale_order_date = fields.Datetime("Sale Order Date")
    delivery_date = fields.Datetime("Delivery Date")
    abg_issued_on = fields.Char("ABG Issued On")
    abg_amount = fields.Integer("ABG Amount")
    abg_expiry_date = fields.Datetime("ABG Expiry Date")
    abg_claim_date = fields.Datetime("ABG Claim Date")
    pbg_issued_on = fields.Char("PBG Issued On")
    pbg_amount = fields.Integer("PBG Amount")
    pbg_expiry_date = fields.Datetime("PBG Expiry Date")
    pbg_claim_date = fields.Datetime("PBG Claim Date")
    remarks = fields.Text(string='Remarks')
    abg_duration_time = fields.Datetime("ABG Duration Time")
    pbg_duration_warranty = fields.Datetime("PBG Duration Time")
    is_within_seven = fields.Boolean(compute='_is_within_seven', string='Is Within Seven', help="Check abg or pbg due date is within 7 days of current date.")

    @api.onchange('our_sale_order_no')
    def onchange_member_type(self):
        if self.our_sale_order_no:
            self.partner_id = self.our_sale_order_no.partner_id and self.our_sale_order_no.partner_id.id or False
            self.sale_order_date = self.our_sale_order_no.date_order or False
            self.delivery_date = self.our_sale_order_no.commitment_date or False
            self.abg_duration_time = self.our_sale_order_no.date_order + relativedelta(months=1)

    def _is_within_seven(self):
        for bank_guarantee in self:
            bank_guarantee.is_within_seven = False
            if bank_guarantee.abg_expiry_date or bank_guarantee.pbg_expiry_date:
                today = datetime.today()
                within_seven_date = today + timedelta(days=7)
                if bank_guarantee.abg_expiry_date:
                    if today.date() <= bank_guarantee.abg_expiry_date.date() and bank_guarantee.abg_expiry_date.date() <= within_seven_date.date():
                        bank_guarantee.is_within_seven = True
                if bank_guarantee.pbg_expiry_date:
                    if today.date() <= bank_guarantee.pbg_expiry_date.date() and bank_guarantee.pbg_expiry_date.date() <= within_seven_date.date():
                        bank_guarantee.is_within_seven = True
