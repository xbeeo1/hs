# -*- coding: utf-8 -*-

from odoo import fields, models


class AccountMoveLineInherit(models.Model):
    _inherit = 'account.move.line'

    allowed_category_ids = fields.Many2many(
        'product.category',
        compute='_compute_allowed_categories'
    )

    def _compute_allowed_categories(self):
        for rec in self:
            rec.allowed_category_ids = self.env.user.allowed_product_catg_id