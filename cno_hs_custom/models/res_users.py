# -*- coding: utf-8 -*-

from odoo import fields, models


class ResUsers(models.Model):
    _inherit = 'res.users'

    allowed_product_catg_id = fields.Many2many(
        comodel_name='product.category',
        string='Allowed Product Catg',
        help='Allowed Product Catg for this user'
    )

    allowed_warehouse_id = fields.Many2many(
        comodel_name='stock.warehouse',
        string='Allowed Warehouse',
        help='Allowed Warehouse for this user'
    )

    def write(self, values):
        res = super().write(values)
        fields_to_check = ['allowed_product_catg_id', 'allowed_warehouse_id']

        if self.ids and any(field in values for field in fields_to_check):
            self.env.registry.clear_cache()
        return res
