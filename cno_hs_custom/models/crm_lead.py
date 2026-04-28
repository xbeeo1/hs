# -*- coding: utf-8 -*-
from openpyxl.worksheet import related

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class CrmLeadInherit(models.Model):
    _inherit = 'crm.lead'

    reference = fields.Char('Reference', copy=False, readonly=True, default=lambda s: s.env._('New'))
    bank_name = fields.Many2one(comodel_name='res.bank', string='Bank Name', required=True)
    account_title = fields.Char(string='Account Title', required=True)
    account_number = fields.Char(string='Account Number', required=True)
    sms_text = fields.Char(string='SMS Text')
    purchase_count = fields.Integer(string="Purchase Order", compute='_purchase_total')
    bag_type = fields.Selection([('pp', 'PP'), ('Jute', 'Jute')], default='pp',required=True)
    no_bags = fields.Integer(string='No. of Bags', compute='_no_bags',store=True)
    tokan_date = fields.Date(string = 'Date', required=True)
    amount = fields.Float(string='CDR Amount', required=True)
    cdr_no = fields.Char(string='CDR No.')
    no_of_acers = fields.Float(string='No. of Acers',required=True)
    grain_weight = fields.Float(string='Grain Weight', compute='_grain_weight',store=True)
    cdr_status = fields.Selection([('pending','Pending'),('received','Received')], default='pending',string='CDR Status')
    tokan_number = fields.Char(string='Tokan Number',required=True)
    whatsapp_num = fields.Char(string='WhatsApp Number', related="partner_id.whatsapp_num",readonly=True )

    @api.depends('no_of_acers', 'bag_type')
    def _no_bags(self):
        for x in self:
            if x.no_of_acers:
                if x.bag_type == 'pp':
                    x.no_bags = x.no_of_acers * 20
                else:
                    x.no_bags = x.no_of_acers * 10
            else:
                x.no_bags = 0.0



    @api.depends('no_bags','bag_type')
    def _grain_weight(self):
        for x in self:
            if x.no_bags:
                if x.bag_type == 'pp':
                    x.grain_weight = x.no_bags * 50
                else:
                    x.grain_weight = x.no_bags * 100
            else:
                x.grain_weight = 0.0

    @api.constrains('amount')
    def _check_amount(self):
        for rec in self:
            if rec.amount == 0.0:
                raise ValidationError(" Amount should be greater than 0.")

    # @api.constrains('no_of_acers')
    # def _check_no_of_acers(self):
    #     for rec in self:
    #         if rec.no_of_acers > 10.0:
    #             raise ValidationError(" No of acers cannot be greater than 10.")
    #         if rec.no_of_acers == 0.0:
    #             raise ValidationError("No of acers should be greater than 0.")

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



    # @api.model_create_multi
    # def create(self, vals_list):
    #     for vals in vals_list:
    #         if not vals.get('reference') or vals['reference'] == _('New'):
    #             vals['reference'] = self.env['ir.sequence'].next_by_code('crm.lead') or _('New')
    #     return super().create(vals_list)


    def action_purchase_order_new(self):
        self.ensure_one()
        if not self.cdr_no:
            raise ValidationError('Fill out CDR No.')
        if self.cdr_status != 'received':
            raise ValidationError('CDR status should be received.')
        order_lines = []
        grain_obj = self.env['grain.product'].search([])
        if not grain_obj:
            raise ValidationError("Please add Grain Product")
        if grain_obj:
            order_lines.append((0, 0, {
                'product_id': grain_obj.product_id.id,
                'product_qty': self.grain_weight or 1,
                'product_uom_id': grain_obj.product_id.uom_id.id or '',
            }))

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
                'default_reference': self.tokan_number,
                'default_crm_lead_id': self.id,

                'default_order_line': order_lines,

            }
        }