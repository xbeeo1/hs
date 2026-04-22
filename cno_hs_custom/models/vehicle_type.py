# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.exceptions import ValidationError


class Vehicletype(models.Model):
    _name = "vehicle.type"
    _description = "Vehicle Type"

    name = fields.Char(string="Name")



    """CREATE METHOD FOR VALIDATION ON DUPLICATION Village"""
    def create(self, vals):
        if 'name' in vals:
            existing_name = self.search([('name', '=', vals['name'])], limit=1)
            if existing_name:
                raise ValidationError("Vehicle Already Exist.")
        return super(Vehicletype, self).create(vals)
