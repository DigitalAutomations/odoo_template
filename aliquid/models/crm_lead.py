from odoo import api, models, fields


class CrmLeadInh(models.Model):
    _inherit = 'crm.lead'

    partner_address_email = fields.Char('Partner Contact Email')

