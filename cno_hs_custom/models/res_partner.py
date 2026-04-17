from odoo import models , api ,fields,_
from odoo.exceptions import ValidationError

class ResPartnerInherit(models.Model):
    _inherit = "res.partner"

    is_farmer = fields.Boolean(string="Is Farmer",required=True)
    cnic = fields.Char(string="CNIC",required=True)
    village_id = fields.Many2one("farmer.village", string="Village",required=True)
    reference = fields.Char('Reference', copy=False, readonly=True, default=lambda s: s.env._('New'))



    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('reference') or vals['reference'] == _('New'):
                vals['reference'] = self.env['ir.sequence'].next_by_code('farmer.seq.no') or _('New')
        return super().create(vals_list)
