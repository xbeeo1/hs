# -*- coding: utf-8 -*-

from odoo import fields, models,api


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    allowed_category_ids = fields.Many2many(
        'product.category',
        compute='_compute_allowed_categories'
    )

    conversion_value = fields.Float(string="Conversion Value",compute='_compute_conversion_value',store=True)
    conversion_uom_id = fields.Many2one("uom.uom", string="Converted UOM", related='product_id.conversion_uom_id',
                                        store=True)

    def _compute_allowed_categories(self):
        for rec in self:
            rec.allowed_category_ids = self.env.user.allowed_product_catg_id


    @api.onchange('product_id', 'price_unit')
    def _ensure_negative_price(self):
        for line in self:
            if line.product_id.is_price_negative and line.price_unit > 0:
                line.price_unit = -abs(line.price_unit)

    @api.model
    def create(self, vals):
        if 'product_id' in vals:
            product = self.env['product.product'].browse(vals['product_id'])
            if product.is_price_negative and vals.get('price_unit', 0) > 0:
                vals['price_unit'] = -abs(vals['price_unit'])
        return super().create(vals)

    def write(self, vals):
        res = super().write(vals)
        for line in self:
            if line.product_id.is_price_negative and line.price_unit > 0:
                line.price_unit = -abs(line.price_unit)
        return res

    @api.depends('product_qty', 'product_id')
    def _compute_conversion_value(self):
        for rec in self:
            factor = rec.product_id.conversion_value or 0.0
            if factor > 0:
                rec.conversion_value = rec.product_qty / factor
            else:
                rec.conversion_value = 0.0