# -*- coding: utf-8 -*-

from odoo import fields, models


class ResUsers(models.Model):
    _inherit = 'res.users'

    allowed_product_catg_id = fields.Many2many(
        comodel_name='product.category',
        string='Allowed Product Catg',
        help='Allowed Product Catg for this user'
    )

    def write(self, values):
        res = super(ResUsers, self).write(values)
        if self.ids and 'allowed_product_catg_id' in values:
            self.env.registry.clear_cache()
        return res
