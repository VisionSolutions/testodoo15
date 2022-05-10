# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from collections import defaultdict
from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.addons.stock.models.stock_rule import ProcurementException
from odoo.tools import float_compare, OrderedSet
from odoo.addons.mrp.models.stock_orderpoint import StockWarehouseOrderpoint


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    ga_drawing = fields.Selection([
        ('approved', 'Approved'),
        ('approval_pending', 'Approval Pending')], string='GA Drawing', default='approval_pending')
    ga_approval_date = fields.Datetime("GA Approval Date")
    load_data_drawing = fields.Selection([
        ('approved', 'Approved'),
        ('approval_pending', 'Approval Pending')], string='Load Data Drawing', default='approval_pending')
    electrical_circuit_diagram = fields.Selection([
        ('approved', 'Approved'),
        ('approval_pending', 'Approval Pending')], string='Electrical Circuit Diagram', default='approval_pending')
    electrical_circuit_approval_date = fields.Datetime("Electrical Circuit Approval Date")
    hydraulics_circuit_diagram = fields.Selection([
        ('approved', 'Approved'),
        ('approval_pending', 'Approval Pending')], string='Hydraulics Circuit Diagram', default='approval_pending')
    qap_sent = fields.Boolean('QAP Sent')
    qap_approval = fields.Boolean('QAP Approval')
    qap_approval_on_date = fields.Datetime("QAP Approval On")
    equipment_number = fields.Char("Equipment Number")
    sale_order_id = fields.Many2one('sale.order', 'Sales Order')
    transport = fields.Selection(related="sale_order_id.transport", string='Delivery INCOTERM',)
    panel_drawing_no = fields.Char("Panel Drawing No")
    ga_drg_no = fields.Char("GA Drg. No")

    @api.model
    def create(self, vals):
        rec = super(MrpProduction, self).create(vals)
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

    def action_confirm(self):
        for production in self:
            if not production.ga_drawing == 'approved':
                raise UserError(_('The GA Drawing Field should be approved.'))
            elif not production.ga_approval_date:
                raise UserError(_('The GA Approval Date Field should be selected.'))
            elif not production.load_data_drawing == 'approved':
                raise UserError(_('The Load Data Drawing Field should be approved.'))
            elif not production.qap_sent:
                raise UserError(_('The QAP Sent Field should be ticked.'))
            elif not production.qap_approval:
                raise UserError(_('The QAP Approval Field should be ticked.'))
            elif not production.qap_approval_on_date:
                raise UserError(_('The QAP Approval On Date Field should be selected.'))
            elif not production.electrical_circuit_diagram == 'approved':
                raise UserError(_('The Electrical Circuit Diagram Field should be approved.'))
            elif not production.electrical_circuit_approval_date:
                raise UserError(_('The Electrical Circuit Approval Date Field should be selected.'))
            elif not production.hydraulics_circuit_diagram == 'approved':
                raise UserError(_('The Hydraulics Circuit Diagram Field should be approved.'))
            elif not production.equipment_number:
                raise UserError(_('The Equipment Number Field should be selected.'))
            else:
                continue
        return super(MrpProduction, self).action_confirm()

    def button_plan(self):
        for production in self:
            if not production.ga_drawing == 'approved':
                raise UserError(_('The GA Drawing Field should be approved.'))
            elif not production.ga_approval_date:
                raise UserError(_('The GA Approval Date Field should be selected.'))
            elif not production.load_data_drawing == 'approved':
                raise UserError(_('The Load Data Drawing Field should be approved.'))
            elif not production.qap_sent:
                raise UserError(_('The QAP Sent Field should be ticked.'))
            elif not production.qap_approval:
                raise UserError(_('The QAP Approval Field should be ticked.'))
            elif not production.qap_approval_on_date:
                raise UserError(_('The QAP Approval On Date Field should be selected.'))
            elif not production.electrical_circuit_diagram == 'approved':
                raise UserError(_('The Electrical Circuit Diagram Field should be approved.'))
            elif not production.electrical_circuit_approval_date:
                raise UserError(_('The Electrical Circuit Approval Date Field should be selected.'))
            elif not production.hydraulics_circuit_diagram == 'approved':
                raise UserError(_('The Hydraulics Circuit Diagram Field should be approved.'))
            elif not production.equipment_number:
                raise UserError(_('The Equipment Number Field should be selected.'))
            else:
                continue
        return super(MrpProduction, self).button_plan()


class StockRule(models.Model):
    _inherit = 'stock.rule'

    @api.model
    def _run_manufacture(self, procurements):
        productions_values_by_company = defaultdict(list)
        errors = []
        for procurement, rule in procurements:
            if float_compare(procurement.product_qty, 0, precision_rounding=procurement.product_uom.rounding) <= 0:
                # If procurement contains negative quantity, don't create a MO that would be for a negative value.
                continue
            bom = rule._get_matching_bom(procurement.product_id, procurement.company_id, procurement.values)

            productions_values_by_company[procurement.company_id.id].append(rule._prepare_mo_vals(*procurement, bom))

        if errors:
            raise ProcurementException(errors)

        for company_id, productions_values in productions_values_by_company.items():
            # create the MO as SUPERUSER because the current user may not have the rights to do it (mto product launched by a sale for example)
            productions = self.env['mrp.production'].with_user(SUPERUSER_ID).sudo().with_company(company_id).create(productions_values)
            self.env['stock.move'].sudo().create(productions._get_moves_raw_values())
            self.env['stock.move'].sudo().create(productions._get_moves_finished_values())
            productions._create_workorder()
            # productions.filtered(lambda p: not p.orderpoint_id).action_confirm()

            for production in productions:
                origin_production = production.move_dest_ids and production.move_dest_ids[0].raw_material_production_id or False
                orderpoint = production.orderpoint_id
                if orderpoint and orderpoint.create_uid.id == SUPERUSER_ID and orderpoint.trigger == 'manual':
                    production.message_post(
                        body=_('This production order has been created from Replenishment Report.'),
                        message_type='comment',
                        subtype_xmlid='mail.mt_note')
                elif orderpoint:
                    production.message_post_with_view(
                        'mail.message_origin_link',
                        values={'self': production, 'origin': orderpoint},
                        subtype_id=self.env.ref('mail.mt_note').id)
                elif origin_production:
                    production.message_post_with_view(
                        'mail.message_origin_link',
                        values={'self': production, 'origin': origin_production},
                        subtype_id=self.env.ref('mail.mt_note').id)
        return True


class StockWarehouseOrderpoint(models.Model):
    _inherit = 'stock.warehouse.orderpoint'

    def _post_process_scheduler(self):
        pass

    StockWarehouseOrderpoint._post_process_scheduler = _post_process_scheduler
