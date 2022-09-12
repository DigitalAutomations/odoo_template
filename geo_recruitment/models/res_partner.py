
from odoo import fields,models,api,_


class ResPartner(models.Model):
    _inherit = 'res.partner'

    user_id = fields.Many2one('res.users', string='Account Manager',
                              help='The internal user in charge of this contact.')