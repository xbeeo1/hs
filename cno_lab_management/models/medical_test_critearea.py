# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.
from email.policy import default

from odoo import api, fields, models, _
# classes under cofigration menu of laboratry
from odoo.exceptions import ValidationError

class medical_test_critearea(models.Model):
    _name  = 'medical_test.critearea'
    _description = 'medical test critearea'

    test_id = fields.Many2one('medical.test_type',)
    name = fields.Char('Specifications',)
    seq = fields.Integer('Sequence')
    medical_test_type_id = fields.Many2one ('medical.test_type', 'Test Type')
    medical_lab_id = fields.Many2one('medical.lab', 'Medical Lab Result')
    warning  = fields.Boolean('Warning')
    excluded  = fields.Boolean('Excluded')
    lower_limit = fields.Float('Lower Limit')
    upper_limit = fields.Float('Upper Limit')
    lab_test_unit_id = fields.Many2one('medical.lab.test.units', 'Units')
    result = fields.Float('Result')
    result_text =  fields.Char('Result Text')
    gram =  fields.Float('Gram')
    percentage =  fields.Float('Percentage')
    normal_range =  fields.Char('Limit')
    limit_int = fields.Integer('Limit Integer')
    remark = fields.Text('Remarks')
    bag_dhang = fields.Char('No of Bag in Dhang')
    no_of_bag_drawn = fields.Integer('No of Bags Drawn')
    weight_1 = fields.Float('1st Bag')
    weight_2 = fields.Float('2nd Bag')
    weight_3 = fields.Float('3rd Bag')
    weight_4 = fields.Float('4th Bag')
    avg_weight = fields.Float('Avg Weight')
    moisture_per = fields.Float('Moisture%')
    trash_statust = fields.Char('Trash Statust')
    is_below_limit = fields.Boolean('Is Below Limit',default=False)

    is_avg_weight= fields.Boolean('Is Below Limit',default=False)

    @api.onchange('gram')
    def _onchange_gram_percentage(self):
        for rec in self:
            if rec.medical_lab_id and rec.medical_lab_id.test_id.auto_per_calculation:
                sample_weight = rec.medical_lab_id.sample_weight_gram or 0.0
                if sample_weight:
                    if rec.gram > sample_weight:
                        raise ValidationError('Gram value should be less than sample weight')
                    rec.percentage = (rec.gram / sample_weight) * 100
                else:
                    rec.percentage = 0.0

    @api.onchange('weight_1','weight_2','weight_3','weight_4')
    def _onchange_avg_weight(self):
        for rec in self:
            bag_weight = rec.medical_lab_id.standard_bag_weight or 0.0
            if bag_weight:
                total_weight = rec.weight_1 + rec.weight_2 + rec.weight_3 +rec.weight_4
                rec.avg_weight = total_weight / 4
            else:
                rec.avg_weight = 0.0

    @api.onchange('percentage')
    def _is_below_limit(self):
        for rec in self:
            if rec.medical_lab_id and rec.medical_lab_id.test_id and rec.medical_lab_id.test_id.auto_per_calculation:
                if rec.percentage > rec.limit_int:
                    rec.is_below_limit = True
                else:
                    rec.is_below_limit = False
            else:
                rec.is_below_limit = False

    @api.onchange('avg_weight')
    def _is_avg_limit(self):
        for rec in self:
            bag_weight = rec.medical_lab_id.standard_bag_weight or 0.0
            if bag_weight > rec.avg_weight:
                rec.is_avg_weight = True
            else:
                rec.is_avg_weight = False



