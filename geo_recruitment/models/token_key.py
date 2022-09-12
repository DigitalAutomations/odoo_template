from odoo import models, fields, api


class LinkedinConfiguration(models.Model):
    _name = 'linkedin.configuration'
    token_key = fields.Char('Token Key')
    active = fields.Boolean('Active')

