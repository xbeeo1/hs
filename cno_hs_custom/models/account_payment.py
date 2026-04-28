# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class AccountPaymentInherit(models.Model):
    _inherit = "account.payment"

    current_balance = fields.Float(compute='_compute_current_balance', string='Balance')
    remaining_balance = fields.Float(compute='_compute_remaining_balance', string='Remaining Balance')

    @api.depends('journal_id')
    def _compute_current_balance(self):
        account_id = self.journal_id.default_account_id
        balances = {
            account.id: balance
            for account, balance in self.env['account.move.line']._read_group(
                domain=[('account_id', 'in', account_id.ids), ('parent_state', '=', 'posted'),
                        ('company_id', '=', self.env.company.id)],
                groupby=['account_id'],
                aggregates=['balance:sum'],
            )
        }
        for record in self:
            record.current_balance = balances.get(account_id.id, 0)

    @api.depends('current_balance', 'amount')
    def _compute_remaining_balance(self):
        for x in self:
            x.remaining_balance = x.current_balance - x.amount

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        for rec in records:
            if rec.current_balance < 0:
                raise ValidationError(_("You have insufficient balance!"))
        return records

    def write(self, vals):
        res = super().write(vals)
        for rec in self:
            if rec.current_balance < 0:
                raise ValidationError(_("You have insufficient balance!"))
        return res