# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
# classes under cofigration menu of laboratry 

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
    gram =  fields.Char('Gram')
    percentage =  fields.Char('Percentage')
    normal_range =  fields.Char('Limit')
    limit_int = fields.Integer('Limit Integer')
    remark = fields.Text('Remarks')
    bag_dhang = fields.Char('Bag Dhang')
    no_of_bag_drawn = fields.Integer('No of Bags Drawn')
    weight_1 = fields.Float('1st Weight')
    weight_2 = fields.Float('2nd Weight')
    weight_3 = fields.Float('3rd Weight')
    weight_4 = fields.Float('4rd Weight')
    avg_weight = fields.Float('Avg Weight')
    moisture_per = fields.Float('Moisture%')
    trash_statust = fields.Char('Trash Statust')


