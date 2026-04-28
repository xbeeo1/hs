# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from datetime import date,datetime
from odoo.exceptions import UserError, ValidationError
# classes under  menu of laboratry 

class medical_patient_lab_test(models.Model):
	_name = 'medical.patient.lab.test'
	_description = 'medical patient lab test'
	_rec_name = 'medical_test_type_id'

	request = fields.Char('Request', readonly = True)
	date =  fields.Datetime('Date', default = fields.Datetime.now)
	lab_test_owner_partner_id = fields.Many2one('res.partner', 'Owner Name')
	urgent =  fields.Boolean('Urgent',)
	owner_partner_id = fields.Many2one('res.partner')
	state = fields.Selection([('draft', 'Draft'),('tested', 'Tested'), ('cancel', 'Cancel')], readonly= True, default = 'draft')
	medical_test_type_id = fields.Many2one('medical.test_type', 'Test Type',required = False)
	type = fields.Selection(
		related='medical_test_type_id.type',
		store=True,
		readonly=True
	)
	patient_id = fields.Many2one('res.partner','Farmer' )
	doctor_id = fields.Many2one('res.partner','Lab Analyst',required=True)
	lab_test_lines = fields.One2many('medical.patient.lab.test.line', 'lab_test_id',
	                                 string="Lab Test Line")
	gate_pass_no = fields.Char('Gate Pass No')
	vehicle_number = fields.Char(string='Vehicle Number')
	tokan_no = fields.Char('Tokan No')
	sample_weight_gram = fields.Float(string='Sample weight in (G)')
	stock_picking_id = fields.Many2one('stock.picking','Stock Picking')
	standard_bag_weight = fields.Float(string='Standard Bag Weight',compute='_compute_standard_bag_weight')
	outsourced_lab_request = fields.Boolean(string="Outsourced Lab Request")

	partner_lab_id = fields.Many2one(comodel_name='partner.lab', string="Partner Lab")

	lab_res_created = fields.Boolean(default  =  False)
	bag_type = fields.Selection([('pp', 'PP'), ('Jute', 'Jute')], readonly=True)

	@api.model_create_multi
	def create(self, vals_list):
		for vals in vals_list:
			vals['request'] = self.env['ir.sequence'].next_by_code('test_seq')
		return super(medical_patient_lab_test, self).create(vals_list)

	def _compute_standard_bag_weight(self):
		for rec in self:
			if rec.bag_type:
				if rec.bag_type == 'pp':
					rec.standard_bag_weight = 51
				else:
					rec.standard_bag_weight = 102
			else:
				rec.standard_bag_weight = 0




	def cancel_lab_test(self):
		self.write({'state': 'cancel'})

	def create_lab_test(self):
		res_ids = []
		for browse_record in self:
			result = {}
			medical_lab_obj = self.env['medical.lab']
			res=medical_lab_obj.create({
										'name': self.env['ir.sequence'].next_by_code('ltest_seq'),
									   'patient_id': browse_record.patient_id.id,
									   'date_requested':browse_record.date or False,
									   'test_id':browse_record.medical_test_type_id.id or False,
									   'requestor_physician_id': browse_record.doctor_id.id or False,
									   })
			res_ids.append(res.id)
			if res_ids:                     
				imd = self.env['ir.model.data']
				action = self.env.ref('cno_lab_management.action_medical_lab_form')
				list_view_id = imd.sudo()._xmlid_to_res_id('cno_lab_management.medical_lab_tree_view')
				form_view_id  = imd.sudo()._xmlid_to_res_id('cno_lab_management.medical_lab_form_view')
				result = {
								'name': action.name,
								'help': action.help,
								'type': action.type,
								'views': [ [list_view_id,'list' ],[form_view_id,'form']],
								'target': action.target,
								'context': action.context,
								'res_model': action.res_model,
								'res_id':res.id,
								
							}

			if res_ids:
					result['domain'] = "[('id','=',%s)]" % res_ids

		return result

class MedicalPatientLabTestLine(models.Model):
    _name = "medical.patient.lab.test.line"
    _description = 'medical Prescription order line'

    medical_test_type_id = fields.Many2one('medical.test_type', 'Test Type', required=True)
    lab_test_id = fields.Many2one('medical.patient.lab.test', 'Lab Test')



