# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.orm.decorators import readonly


class PurchaseOrderInherit(models.Model):
    _inherit = 'purchase.order'

    bank_name_id = fields.Many2one(comodel_name='res.bank', string='Bank Name', readonly=True)
    crm_lead_id = fields.Many2one(comodel_name='crm.lead', string='CRM Lead', readonly=True)
    account_title = fields.Char(string='Account Title', readonly=True)
    account_number = fields.Char(string='Account Number', readonly=True)
    sms_text = fields.Char(string='SMS Text')
    reference = fields.Char(string='Tokan No', readonly=True)