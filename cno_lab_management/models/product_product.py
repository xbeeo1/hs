# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ProductProductInherit(models.Model):
    _inherit = 'product.product'

    create_mrp_order = fields.Boolean(string="To Create MRP Order",related='product_tmpl_id.create_mrp_order', store=True)
    done_mrp_order = fields.Boolean(string="Done MRP Order",related='product_tmpl_id.done_mrp_order', store=True)

