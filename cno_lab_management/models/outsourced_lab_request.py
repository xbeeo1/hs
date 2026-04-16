# -*- coding: utf-8 -*-


from odoo import api, fields, models , _
from datetime import date, datetime


class OutsourcedLabRequest(models.Model):
    _name = 'outsourced.lab.request'
    _description = 'Outsourced Lab Request'

    name = fields.Char("Name" , readonly=True)
    date_analysis = fields.Datetime('Date of the Analysis', default=datetime.now() , readonly=True)
    patient_id = fields.Many2one('res.partner', 'Farmer', readonly=True)
    date_requested = fields.Datetime('Date requested', default=datetime.now() , readonly=True)
    requestor_physician_id = fields.Many2one('res.partner', 'Physician',  readonly=True)
    partner_lab_id = fields.Many2one(comodel_name='partner.lab', string="Partner Lab" , readonly=True)
    outsourced_lab_test_lines = fields.One2many('outsourced.lab.test.line', 'outsourced_lab_test_id',
                                     string="Lab Test Line")
    state = fields.Selection([('draft', 'Draft'),
                              ('sample_submitted', 'Sample Submitted'),
                              ('reports_received', 'Reports Received'),
                              ('delivered', 'Delivered')],
                             string='Status', readonly=True, default='draft')





    @api.model_create_multi
    def create(self, vals_list):
        line_vals = []
        result = super(OutsourcedLabRequest, self).create(vals_list)
        for val in vals_list:
            val['name'] = self.env['ir.sequence'].next_by_code('olrtest_seq')

        return result

    def action_sample_submitted(self):
        self.state = 'sample_submitted'

    def action_reports_received(self):
        self.state = 'reports_received'

    def action_delivered(self):
        self.state = 'delivered'




class OutsourcedLabTestLine(models.Model):
    _name = "outsourced.lab.test.line"
    _description = 'outsourced lab test line'

    medical_test_type_id = fields.Many2one('medical.test_type', 'Test Type', required=True)
    outsourced_lab_test_id = fields.Many2one('outsourced.lab.request', 'Lab Test')