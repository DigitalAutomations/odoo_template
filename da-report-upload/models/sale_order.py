# -*- coding: utf-8 -*-

from odoo import fields, models

#_logger = logging.getLogger(__name__)

class SaleOrderDa(models.Model):
    _inherit = 'sale.order'

    indirect_partner_id = fields.Many2one( 'res.partner', string = 'Cliente Indiretto', required = False, default = None )
    title               = fields.Char( string = 'Titolo', required = False, default = None )
    num_offerta_stesi   = fields.Char( string = 'N° Offerta', required = False, default = None )

