# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import date, datetime, timedelta
from odoo.exceptions import UserError ,ValidationError

class StockPickingInherit(models.Model):
    _inherit = 'stock.picking'
    _description = 'stock.picking.inherit'

    bank_name = fields.Many2one(comodel_name='res.bank', string='Bank Name', readonly=True)
    account_title = fields.Char(string='Account Title', readonly=True)
    account_number = fields.Char(string='Account Number', readonly=True)
    sms_text = fields.Char(string='SMS Text', readonly=True)
    reference = fields.Char(string='Tokan No', readonly=True)
    vehicle_type_id = fields.Many2one(comodel_name='vehicle.type', string='Vehicle Type')
    vehicle_number = fields.Char(string='Vehicle Number')
    vehicle_image = fields.Binary(string='Vehicle Image')
    driver_name = fields.Char(string='Driver Name')
    driver_ph_number = fields.Char(string='Driver Phone Number')
    driver_cnic = fields.Char(string='Driver CNIC')
    driver_image = fields.Binary(string='Driver Image')
    warehouse_id = fields.Many2one(comodel_name='stock.warehouse', string='Warehouse')
    total_bags = fields.Integer(string='Total Bags')
    first_weight = fields.Float(string='First Weight')
    second_weight = fields.Float(string='Second Weight')
    net_weight = fields.Float(string='Net Weight')
    nunber = fields.Char(string='Number')
    e_number = fields.Char(string='E Number')
    date_in = fields.Datetime(string='Date In')
    date_out = fields.Datetime(string='Date Out')
    bag_type = fields.Selection([('pp', 'PP'),('Jute', 'Jute')])
    lab_request_count = fields.Integer(string="Lab Request Count", compute='_lab_total')

    state = fields.Selection([
        ('draft', 'Draft'),
        ('waiting', 'Waiting Another Operation'),
        ('confirmed', 'Waiting'),
        ('assigned', 'Ready'),
        ('unloading', 'Unloading'),
        ('done', 'Done'),
        ('cancel', 'Cancelled'),
        ], string='Status', readonly=True, copy=False, index=True, tracking=True)

    @api.model
    def create(self, vals):
        picking = super().create(vals)
        if picking.origin:
            # Purchase Order fallback
            purchase_order = self.env['purchase.order'].search([('name', '=', picking.origin)], limit=1)
            if purchase_order:
                picking.bank_name = purchase_order.bank_name_id.id if purchase_order.bank_name_id else None
                picking.account_title = purchase_order.account_title
                picking.account_number = purchase_order.account_number
                picking.sms_text = purchase_order.sms_text
                picking.reference = purchase_order.reference

        return picking

    def action_unloading(self):
        for picking in self:
            has_custom_product = any(
                move.product_id.is_custom for move in picking.move_ids
            )

            # Run validation ONLY if custom product exists
            if has_custom_product:
                lab_analysis = self.env['medical.lab'].search_count(
                    [('stock_picking_id', '=', picking.id), ('state', '=', 'approved'),('type','=','lab_analysis')])
                if not lab_analysis:
                    raise ValidationError('Please add Lab Analysis Result')
                random_quality_test = self.env['medical.lab'].search_count(
                    [('stock_picking_id', '=', picking.id), ('state', '=', 'approved'), ('type', '=', 'random_quality_test')])
                if not random_quality_test:
                    raise ValidationError('Please add Random Quality Test')
                missing = []
                if not picking.vehicle_type_id:
                    missing.append("Vehicle Type")
                if not picking.vehicle_number:
                    missing.append("Vehicle Number")
                if not picking.driver_name:
                    missing.append("Driver Name")
                if not picking.driver_ph_number:
                    missing.append("Driver Phone Number")
                if not picking.driver_cnic:
                    missing.append("Driver CNIC")
                if not picking.warehouse_id:
                    missing.append("Warehouse")
                if not picking.total_bags:
                    missing.append("Total Bags")
                if not picking.first_weight:
                    missing.append("First Weight")
                if not picking.nunber:
                    missing.append("Number")
                if not picking.e_number:
                    missing.append("E Number")
                if not picking.date_in:
                    missing.append("Date In")
                if not picking.bag_type:
                    missing.append("Bag Type")

                # Final check
                if missing:
                    raise ValidationError(
                        "Please fill all required fields before validation:\n- " +
                        "\n- ".join(missing)
                    )
        self.state = 'unloading'


    def button_validate(self):
        for picking in self:
            has_custom_product = any(
                move.product_id.is_custom for move in picking.move_ids
            )

            # Run validation ONLY if custom product exists
            if has_custom_product:
                missing = []

                if not picking.second_weight:
                    missing.append("Second Weight")
                if not picking.net_weight:
                    missing.append("Net Weight")
                if not picking.date_out:
                    missing.append("Date Out")

                if missing:
                    raise ValidationError(
                        "Please fill all required fields before validation:\n- " +
                        "\n- ".join(missing)
                    )


                for move in picking.move_ids:
                    po_line = move.purchase_line_id  # IMPORTANT LINK
                    if not po_line:
                        continue
                    demand = po_line.product_qty

                    # total done from all pickings
                    done_qty = sum(
                        self.env['stock.move'].search([
                            ('purchase_line_id', '=', po_line.id),
                            ('state', '=', 'done')
                        ]).mapped('quantity')
                    )

                    new_total = done_qty + move.quantity

                    if new_total > demand:
                        raise ValidationError(
                            f"Demand exceeded for {po_line.product_id.display_name}\n"
                            f"Allowed: {demand}, Already Done: {done_qty}, Trying: {move.quantity}"
                        )

        return super().button_validate()

    def action_lab_request_new(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Lab Request',
            'res_model': 'medical.patient.lab.test',
            'view_mode': 'form',
            'target': 'current',  # or 'new'
            'context': {
                'default_patient_id': self.partner_id.id or None,
                'default_stock_picking_id': self.id or None,
                'default_vehicle_number': self.vehicle_number or '',
                'default_tokan_no': self.reference or None,
                'default_gate_pass_no': self.name or None
            }
        }



    def _lab_total(self):
        for rec in self:
            lab_count = rec.env['medical.lab'].search_count(
                [('stock_picking_id', '=', rec.id),('state', '=', 'approved')])
            rec.lab_request_count = lab_count

    def action_view_lab_result(self):
        self.ensure_one()
        result = {
            "type": "ir.actions.act_window",
            "res_model": "medical.lab",
            "name": _("Lab Result"),
            'view_mode': 'list,form',
            'domain': [('stock_picking_id', '=', self.id),('state', '=', 'approved')],
        }
        return result