# -*- coding: utf-8 -*-

from odoo import fields, models


class GrainProduct(models.Model):
    _name = "grain.product"
    _description = "Grain Product"

    product_id = fields.Many2one(comodel_name='product.product',string='Product')