# -*- coding: utf-8 -*-

from odoo import api, fields, models

class ResPartnerType(models.Model):
    _name = 'res.partner.type'
    _description = 'Partner Type'
    _rec_name = 'label'

    label       = fields.Char( string = 'Nome', required = True )
    description = fields.Text( string = 'Descrizione', required = False, default = None )
    type_id     = fields.One2many(comodel_name="res.partner", inverse_name="type_id", string="Partner")

