# -*- coding: utf-8 -*-

import logging
from odoo import fields, models, api

_logger = logging.getLogger(__name__)

class SaleOrderDa(models.Model):
    _inherit = 'sale.order'

    indirect_partner_id = fields.Many2one( 'res.partner', string = 'Cliente Indiretto', required = False, default = None )
    title               = fields.Char( string = 'Titolo', required = False, default = None )
    num_offerta_stesi   = fields.Char( string = 'N° Offerta', required = False, default = None )
    link                = fields.Char( compute = 'compute_link', store=False )


    def open_form_view(self):
        self.ensure_one()
        form_view = self.env.ref('MODULE.XML_VIEW_ID')
        return {
            'name': _('Sale Order'),
            'res_model': 'sale.order',
            'res_id': self.id,
            'views': [(form_view.id, 'form'), ],
            'type': 'ir.actions.act_window',
            #'target': 'new',
        }

    @api.depends('title')
    def compute_link(self):
        for row in self:
            row.link = '/web#id=' + str( row.id ) + '&action=423&model=sale.order&view_type=form&cids=1&menu_id=259'
