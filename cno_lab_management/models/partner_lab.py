# -*- coding: utf-8 -*-

from odoo import fields, models
from odoo.exceptions import ValidationError


class PartnerLab(models.Model):
    _name = "partner.lab"
    _description = "Partner Lab"

    name = fields.Char(string="Name")


    """CREATE METHOD FOR VALIDATION ON DUPLICATION Village"""
    def create(self, vals):
        if 'name' in vals:
            existing_name = self.search([('name', '=', vals['name'])], limit=1)
            if existing_name:
                raise ValidationError("Partner Lab Already Exist.")
        return super(PartnerLab, self).create(vals)
