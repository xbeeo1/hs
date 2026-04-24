# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.orm.decorators import readonly
from lxml import etree


class PurchaseOrderInherit(models.Model):
    _inherit = 'purchase.order'

    bank_name_id = fields.Many2one(comodel_name='res.bank', string='Bank Name', readonly=True)
    crm_lead_id = fields.Many2one(comodel_name='crm.lead', string='CRM Lead', readonly=True)
    account_title = fields.Char(string='Account Title', readonly=True)
    account_number = fields.Char(string='Account Number', readonly=True)
    sms_text = fields.Char(string='SMS Text')
    reference = fields.Char(string='Tokan No', readonly=True)
    whatsapp_num = fields.Char(string='WhatsApp Number', related="partner_id.whatsapp_num", readonly=True)
    per_maund = fields.Float(string='Per Maund')

    receipt_button_visible = fields.Boolean(
        compute="_compute_receipt_button_visible"
    )

    def _compute_receipt_button_visible(self):
        for order in self:
            resupply_picks = order._get_subcontracting_resupplies()
            order.receipt_button_visible = all(p.state == 'done' for p in resupply_picks)

    @api.onchange('per_maund')
    def _onchange_per_maund(self):
        for order in self:
            for line in order.order_line:
                if order.per_maund > 1 :
                    line.price_unit = order.per_maund / 40

    @api.model
    def get_view(self, view_id=None, view_type='form', **options):
        self.check_access_rights('read')
        result = dict(self._get_view_cache(view_id, view_type, **options))
        node = etree.fromstring(result['arch'])

        if self.env.user.has_group('cno_hs_custom.group_rejistration_access'):
            # Form readonly
            node.set('edit', '0')

            # Fields to make readonly + no_open
            fields_to_disable = [
                'partner_id', 'currency_id', 'picking_type_id', 'user_id', 'company_id',
                'project_id', 'incoterm_id', 'payment_term_id', 'fiscal_position_id', 'bank_name_id'
            ]
            for field_name in fields_to_disable:
                for field in node.xpath(f"//field[@name='{field_name}']"):
                    field.set('readonly', '1')
                    old_options = field.get('options')
                    if old_options:
                        try:
                            options_dict = json.loads(old_options.replace("'", '"'))
                        except:
                            options_dict = {}
                        options_dict['no_open'] = True
                        field.set('options', str(options_dict))
                    else:
                        field.set('options', "{'no_open': True}")

            for field in node.xpath("//field[@name='order_line']//field[@name='product_id']"):
                field.set('readonly', '1')

                old_options = field.get('options')
                if old_options:
                    try:
                        options_dict = json.loads(old_options.replace("'", '"'))
                    except:
                        options_dict = {}
                    options_dict['no_open'] = True
                    field.set('options', str(options_dict))
                else:
                    field.set('options', "{'no_open': True}")
            report_action_id = self.env.ref('purchase.action_report_purchase_order').id
            button_to_disable = ['print_quotation','action_rfq_send','action_purchase_comparison',
                                 'action_acknowledge','action_create_invoice','action_view_picking',
                                 'action_bill_matching','action_view_subcontracting_resupply'
                                 ]

            for button_name in button_to_disable:
                for button in node.xpath(f"//button[@name='{button_name}']"):
                    button.set('invisible', '1')

            for button in node.xpath(f"//button[@name='{report_action_id}']"):
                button.set('invisible', '1')

        result['arch'] = etree.tostring(node, encoding="unicode")
        return result

    def _sync_subcontractor_in_bom(self):
        for order in self:
            partner = order.partner_id
            for line in order.order_line:
                product_tmpl = line.product_id.product_tmpl_id

                # find subcontract BoM
                bom = self.env['mrp.bom'].search([
                    ('product_tmpl_id', '=', product_tmpl.id),
                    ('type', '=', 'subcontract')
                ], limit=1)

                if bom and partner:
                    # avoid duplicates
                    if partner not in bom.subcontractor_ids:
                        bom.write({
                            'subcontractor_ids': [(4, partner.id)]
                        })

    @api.model_create_multi
    def create(self, vals_list):
        orders = super().create(vals_list)
        orders._sync_subcontractor_in_bom()
        return orders