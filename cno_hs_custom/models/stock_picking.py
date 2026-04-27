# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import date, datetime, timedelta
from odoo.exceptions import UserError ,ValidationError
from odoo.orm.decorators import readonly
from lxml import etree
import base64
import requests


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
    driver_cnic_front = fields.Binary(string='Driver CNIC Front')
    driver_cnic_back = fields.Binary(string='Driver CNIC Back')
    warehouse_id = fields.Many2one(comodel_name='stock.warehouse', string='Warehouse')
    cust_location_id = fields.Many2one(comodel_name='stock.location', string='Location',domain="[('warehouse_id', '=', warehouse_id),('usage', '=', 'internal')]")
    total_bags = fields.Integer(string='Total Bags Unloaded')
    first_weight = fields.Float(string='First Weight')
    second_weight = fields.Float(string='Second Weight')
    net_weight = fields.Float(string='Net Weight')
    nunber = fields.Char(string='Gate pass')
    e_number = fields.Char(string='E Number')
    date_in = fields.Datetime(string='Date In')
    date_out = fields.Datetime(string='Date Out')
    bag_type = fields.Selection([('pp', 'PP'),('Jute', 'Jute')], readonly=True)
    lab_request_count = fields.Integer(string="Lab Request Count", compute='_lab_total')

    driver_image_url = fields.Char()
    driver_cnic_front_url = fields.Char()
    driver_cnic_back_url = fields.Char()
    vehicle_image_url = fields.Char()

    state = fields.Selection([
        ('draft', 'Draft'),
        ('waiting', 'Waiting Another Operation'),
        ('confirmed', 'Waiting'),
        ('assigned', 'Pending'),
        ('unloading', 'Unloading'),
        ('done', 'Done'),
        ('cancel', 'Cancelled'),
        ], string='Status', readonly=True, copy=False, index=True, tracking=True)

    allowed_warehouse_ids = fields.Many2many(
        'stock.warehouse',
        compute='_compute_allowed_warehouse'
    )

    def _compute_allowed_warehouse(self):
        for rec in self:
            rec.allowed_warehouse_ids = self.env.user.allowed_warehouse_id

    @api.onchange('cust_location_id')
    def onchange_warehouse_id(self):
        for x in self:
            x.location_dest_id = x.cust_location_id.id

    def copy(self, default=None):
        default = dict(default or {})

        # 🔥 Reset your custom fields
        default.update({
            'vehicle_type_id': False,
            'vehicle_number': False,
            'vehicle_image': False,
            'driver_name': False,
            'driver_ph_number': False,
            'driver_cnic': False,
            'driver_image': False,
            'driver_cnic_front': False,
            'driver_cnic_back': False,
            'cust_location_id': False,
            'warehouse_id': False,
            'total_bags': 0,
            'first_weight': 0.0,
            'second_weight': 0.0,
            'net_weight': 0.0,
            'nunber': False,
            'date_in': False,
            'date_out': False
        })

        return super().copy(default)

    def _get_image_from_url(self, url):
        if not url:
            return False
        try:
            response = requests.get(url, timeout=15)
            if response.status_code == 200:
                return base64.b64encode(response.content)
        except Exception:
            return False
        return False



    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            # IMAGE DOWNLOAD LOGIC
            if vals.get("driver_image_url"):
                vals["driver_image"] = self._get_image_from_url(vals.get("driver_image_url"))

            if vals.get("driver_cnic_front_url"):
                vals["driver_cnic_front"] = self._get_image_from_url(vals.get("driver_cnic_front_url"))

            if vals.get("driver_cnic_back_url"):
                vals["driver_cnic_back"] = self._get_image_from_url(vals.get("driver_cnic_back_url"))

            if vals.get("vehicle_image_url"):
                vals["vehicle_image"] = self._get_image_from_url(vals.get("vehicle_image_url"))

        # create records
        pickings = super().create(vals_list)
        for picking in pickings:
            if picking.origin:
                purchase_order = self.env['purchase.order'].search(
                    [('name', '=', picking.origin)],
                    limit=1
                )

                if purchase_order:
                    picking.bank_name = purchase_order.bank_name_id.id if purchase_order.bank_name_id else False
                    picking.account_title = purchase_order.account_title
                    picking.account_number = purchase_order.account_number
                    picking.sms_text = purchase_order.sms_text
                    picking.reference = purchase_order.reference
                    picking.bag_type = purchase_order.crm_lead_id.bag_type

        return pickings

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
                if not picking.cust_location_id:
                    missing.append("Location")
                if not picking.warehouse_id:
                    missing.append("Warehouse")

                if not picking.total_bags:
                    missing.append("Total Bags")
                if not picking.first_weight:
                    missing.append("First Weight")
                if not picking.nunber:
                    missing.append("Number")
                # if not picking.e_number:
                #     missing.append("E Number")
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
                'default_gate_pass_no': self.nunber or None,
                'default_bag_type': self.bag_type or None,
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

    api.model

    def get_view(self, view_id=None, view_type='form', **options):
        self.check_access_rights('read')
        result = dict(self._get_view_cache(view_id, view_type, **options))
        node = etree.fromstring(result['arch'])

        if self.env.user.has_group('cno_hs_custom.group_weighing_access') or self.env.user.has_group('cno_hs_custom.group_sampling_access'):
            # Form readonly
            node.set('create', '0')
            node.set('delete', '0')

            fields_to_disable = [
                'partner_id', 'location_dest_id', 'picking_type_id', 'owner_id',
                'scheduled_date', 'date_deadline', 'origin']
            for field_name in fields_to_disable:
                for field in node.xpath(f"//field[@name='{field_name}']"):
                    field.set('readonly', '1')
                    old_options = field.get('options')
                    if old_options:
                        try:
                            options_dict = json.loads(old_options.replace("'", '"'))
                        except:
                            options_dict = {}
                        options_dict['no_open'] = True
                        field.set('options', str(options_dict))
                    else:
                        field.set('options', "{'no_open': True}")
            return_action_id = self.env.ref('stock.act_stock_return_picking').id
            report_action_id = self.env.ref('stock.action_report_delivery').id
            button_to_disable = ['action_lab_request_new', 'action_unloading', 'do_print_picking',
                                 'action_cancel', 'action_view_lab_result', 'action_detailed_operations',
                                 'action_open_picking_client_action','action_see_packages'
                                 ]

            for button_name in button_to_disable:
                for button in node.xpath(f"//button[@name='{button_name}']"):
                    button.set('invisible', '1')

            for page in node.xpath("//page[@name='extra']"):
                page.set('invisible', '1')

            for button in node.xpath(f"//button[@name='{return_action_id}']"):
                button.set('invisible', '1')

            for button in node.xpath(f"//button[@name='{report_action_id}']"):
                button.set('invisible', '1')

            if self.env.user.has_group('cno_hs_custom.group_sampling_access'):
                node.set('edit', '0')

                button_to_disable = ['action_lab_request_new','action_view_lab_result']

                for button_name in button_to_disable:
                    for button in node.xpath(f"//button[@name='{button_name}']"):
                        button.set('invisible', '0')



        result['arch'] = etree.tostring(node, encoding="unicode")
        return result

