# -*- coding: utf-8 -*-

from odoo import api, fields, models



class ProductTemplateInheritFRM(models.Model):
    _inherit = 'product.template'

    create_mrp_order = fields.Boolean(string="To Create MRP Order")
    done_mrp_order = fields.Boolean(string="Done MRP Order")
    is_custom = fields.Boolean(string='Is Custom')
    bardana_weight = fields.Float(string='Product Weight')
    filled_bardana_weight = fields.Float(string='Filled Product Weight')



