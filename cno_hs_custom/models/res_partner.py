from odoo import models , api ,fields
from odoo.exceptions import ValidationError

class ResPartnerInherit(models.Model):
    _inherit = "res.partner"

    is_farmer = fields.Boolean(string="Is Farmer",required=True)
    cnic = fields.Char(string="CNIC",required=True)
    village_id = fields.Many2one("farmer.village", string="Village",required=True)
    seq_no = fields.Char("Seq No.", default="New", readonly=True)

    def create(self, values):
        values['seq_no'] = self.env['ir.sequence'].next_by_code('farmer_seq_no') or ''
        return super(ResPartnerInherit, self).create(values)
