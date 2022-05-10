# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class ResPartner(models.Model):
    _inherit = 'res.partner'

    pan_no = fields.Char("PAN NO.")
    gst_filling_frequency = fields.Char("GST Filling Frequency.")
