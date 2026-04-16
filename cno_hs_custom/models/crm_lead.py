# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class CrmLeadInherit(models.Model):
    _inherit = 'crm.lead'

    reference = fields.Char(string='Order Reference', readonly=True,
                            default="New")
    bank_name = fields.Many2one(comodel_name='res.bank', string='Bank Name', required=True)
    account_title = fields.Char(string='Account Title', required=True)
    account_number = fields.Char(string='Account Number', required=True)
    sms_text = fields.Char(string='SMS Text', required=True)
    purchase_count = fields.Integer(string="Purchase Order", compute='_purchase_total')



    def _purchase_total(self):
        for rec in self:
            purchase_count = rec.env['purchase.order'].search_count(
                [('crm_lead_id', '=', rec.id)])
            rec.purchase_count = purchase_count



    def action_view_purchase(self):
        self.ensure_one()
        result = {
            "type": "ir.actions.act_window",
            "res_model": "purchase.order",
            "name": _("Purchase Order"),
            'view_mode': 'list,form',
            'domain': [('crm_lead_id', '=', self.id)],
        }
        return result



    """CREATE CRM SEQUENCE NUMBER"""

    def create(self, values):
        values['reference'] = self.env['ir.sequence'].next_by_code('crm.lead') or ''
        return super(CrmLeadInherit, self).create(values)


    def action_purchase_order_new(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Purchase Order',
            'res_model': 'purchase.order',
            'view_mode': 'form',
            'target': 'current',  # or 'new'
            'context': {
                'default_partner_id': self.partner_id.id or None,
                'default_bank_name_id': self.bank_name.id,
                'default_account_title': self.account_title,
                'default_account_number': self.account_number,
                'default_sms_text': self.sms_text,
                'default_reference': self.reference,
                'default_lead_id': self.id,

            }
        }