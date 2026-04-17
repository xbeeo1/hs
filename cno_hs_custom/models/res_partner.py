from odoo import models , api ,fields,_
from odoo.exceptions import ValidationError

class ResPartnerInherit(models.Model):
    _inherit = "res.partner"

    is_farmer = fields.Boolean(string="Is Farmer")
    is_doctor = fields.Boolean(string="Is Doctor")
    cnic = fields.Char(string="CNIC",required=True)
    village_id = fields.Many2one("farmer.village", string="Village",required=True)
    farmer_ref = fields.Char('Farmer Reference', copy=False, readonly=True, default=lambda s: s.env._('New'))



    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('farmer_ref') or vals['farmer_ref'] == _('New'):
                vals['farmer_ref'] = self.env['ir.sequence'].next_by_code('farmer.seq.no') or _('New')
        return super().create(vals_list)
