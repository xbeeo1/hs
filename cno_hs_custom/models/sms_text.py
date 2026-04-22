# -*- coding: utf-8 -*-

from odoo import fields, models


class SmsText(models.Model):
    _name = "sms.text"
    _description = "SMS Text"

    name = fields.Char(string="SMS")