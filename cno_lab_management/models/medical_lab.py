# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from datetime import date,datetime
# classes under  menu of laboratry 

class medical_lab(models.Model):

    _name = 'medical.lab'
    _description = 'Medical Lab'
 

    name = fields.Char(string="Name", readonly=True, default='/')
    test_id = fields.Many2one('medical.test_type', 'Test name', required = True)
    type = fields.Selection(
        related='test_id.type',
        store=True,
        readonly=True
    )
    date_analysis =  fields.Datetime('Date of the Analysis' , default = datetime.now())
    patient_id = fields.Many2one('res.partner','Farmer', required = True)
    date_requested = fields.Datetime('Date requested',  default = datetime.now())
    requestor_physician_id = fields.Many2one('res.partner','Physician', required = True)
    critearea_ids = fields.One2many('medical_test.critearea','medical_lab_id', 'Critearea')
    results= fields.Text('Results')
    diagnosis = fields.Text('Diagnosis')
    stock_picking_id = fields.Many2one('stock.picking', 'Stock Picking')
    gate_pass_no = fields.Char('Gate Pass No')
    vehicle_number = fields.Char(string='Vehicle Number')
    tokan_no = fields.Char('Tokan No')
    sample_weight_gram = fields.Float(string='Sample Weight in Gram')
    standard_bag_weight = fields.Float(string='Standard Bag Weight')


    state = fields.Selection([('draft','Draft'),('approved','Approved'),('rejected','Rejected'),('cancelled','Cancelled')])



    @api.model_create_multi
    def create(self, vals_list):

        for vals in vals_list:
            if not vals.get('name'):
                vals['name'] = self.env['ir.sequence'].next_by_code('ltest_seq') or '/'

        records = super(medical_lab, self).create(vals_list)

        for rec in records:
            if rec.test_id:
                criterea_ids = self.env['medical_test.critearea'].search([
                    ('test_id', '=', rec.test_id.id)
                ])
                criterea_ids.write({'medical_lab_id': rec.id})

        for vals in vals_list:
            if vals.get('test_id'):
                test = self.env['medical.test_type'].browse(vals['test_id'])
                product = test.service_product_id

                if product and product.create_mrp_order:
                    bom_count = self.env['mrp.bom'].search([
                        ('product_tmpl_id', '=', product.product_tmpl_id.id)
                    ])

                    if bom_count:
                        bom_temp = self.env['mrp.bom'].search([
                            ('product_tmpl_id', '=', product.product_tmpl_id.id),
                            ('product_id', '=', False)
                        ])

                        bom_prod = self.env['mrp.bom'].search([
                            ('product_id', '=', product.id)
                        ])

                        if bom_prod:
                            bom = bom_prod[0]
                        elif bom_temp:
                            bom = bom_temp[0]
                        else:
                            bom = False

                        if bom:
                            mrp_vals = {
                                'origin': vals.get('name'),
                                'product_id': product.id,
                                'product_tmpl_id': product.product_tmpl_id.id,
                                'product_uom_id': product.uom_id.id,
                                'product_qty': 1,
                                'bom_id': bom.id,
                            }

                            mrp = self.env['mrp.production'].sudo().create(mrp_vals)

                            if product.done_mrp_order:
                                mrp.button_mark_done()


        return records


