# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ProductProductInherit(models.Model):
    _inherit = 'product.product'

    is_custom = fields.Boolean(string='Is Custom' ,related='product_tmpl_id.is_custom', store=True)
    create_mrp_order = fields.Boolean(string="To Create MRP Order",related='product_tmpl_id.create_mrp_order', store=True)
    done_mrp_order = fields.Boolean(string="Done MRP Order",related='product_tmpl_id.done_mrp_order', store=True)
    bardana_weight = fields.Float(string='Bardana Weight',related='product_tmpl_id.bardana_weight', store=True)
    filled_bardana_weight = fields.Float(string='Filled bardana Weight',related='product_tmpl_id.filled_bardana_weight', store=True)
    total_bardana_weight = fields.Float(string='T.B Weight',compute='_compute_total_bardana_weight')
    net_grain_weight = fields.Float(string='Net Grain Weight',compute='_compute_net_grain_weight')
    conversion_value = fields.Float(string="Conversion Value",related='product_tmpl_id.conversion_value', store=True)
    conversion_uom_id = fields.Many2one("uom.uom", string="Converted UOM",related='product_tmpl_id.conversion_uom_id', store=True)
    is_price_negative = fields.Boolean(string='Is Price Negative',related='product_tmpl_id.is_price_negative', store=True)


    def _compute_total_bardana_weight(self):
        for rec in self:
            if rec.qty_available and rec.filled_bardana_weight and rec.bardana_weight:
                rec.total_bardana_weight = (rec.qty_available/rec.filled_bardana_weight)* rec.bardana_weight
            else:
                rec.total_bardana_weight = 0.0

    def _compute_net_grain_weight(self):
        for rec in self:
            if rec.qty_available and rec.total_bardana_weight:
                rec.net_grain_weight = rec.qty_available  - rec.total_bardana_weight
            else:
                rec.net_grain_weight = 0.0


