# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class AccountMove(models.Model):
    _inherit = "account.move"

    transporter_name = fields.Char("Transporter Name")
    lr_no = fields.Char("LR No.")


class StockPicking(models.Model):
    _inherit = "stock.picking"

    transporter_name = fields.Char("Transporter Name")
