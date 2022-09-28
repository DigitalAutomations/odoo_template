# -*- coding: utf-8 -*-

from odoo import fields, models

#_logger = logging.getLogger(__name__)

class ResPartnerType(models.Model):
    _inherit = 'res.partner'

    type_id    = fields.Many2one( 'res.partner.type', string = 'Tipologia', required = False, default = None )

