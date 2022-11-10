# -*- coding: utf-8 -*-

import logging, json
from datetime import datetime
from xlrd import open_workbook
import base64
import io
from odoo import api, fields, models
_logger = logging.getLogger(__name__)

from .classes.Parser  import Parser
from .classes.Builder import Builder


class DaReports(models.Model):
    _name = 'da.reports'
    _description = 'Da Reports'

    create_date = fields.Datetime( string = 'Creato il', readonly = True )

    report      = fields.Binary( string = 'Report', required = True )
    file_name   = fields.Char( string = 'File Name', required = False )
    note        = fields.Text( string = 'Note', required = False, default = None )
    log         = fields.Text( string = 'Log', required = False, default = None )
    status      = fields.Char( string = 'Stato', required = True, default = 'uploaded' )
    log         = fields.Text( string = 'log', required = False, default = None )
    sale_orders = fields.Many2many( 'sale.order', 'report_sale_order_rel', 'report_id', 'sale_order_id', string = 'Ordini di vedita' )
    log_text    = fields.Char( string="Log", compute = 'compute_log', store=False )

    @api.depends('log')
    def compute_log(self):
        for row in self:
            log_text = ''
            for line in json.loads( self.log ):
                log_text += line + "<br/>"
            #row.log_text = json.dumps(self.log, indent=4, sort_keys=False)
            self.log_text = log_text

    @api.model
    def create(self, vals):
        rec = super(DaReports, self).create(vals)
        #self.ensure_one()
        row = self.env['da.reports'].search( [ ( 'id', '=', rec.id ) ], limit = 1 )
        parser = Parser.parse( row.report, self.env )

        #_logger.info( json.dumps( parser.header, indent = 4 ) )
        #_logger.info( json.dumps( parser.block1, indent = 4 ) )
        #_logger.info( json.dumps( parser.block2, indent = 4 ) )
        #_logger.info( json.dumps( parser.block3, indent = 4 ) )
        #_logger.info( json.dumps( parser.block4, indent = 4 ) )
        #_logger.info( json.dumps( parser.block5, indent = 4 ) )

        builder = Builder.build( parser, self.env )
        log = parser.logs + builder.logs
        orders = builder.orders
        sale_orders = []
        for order in orders:
            sale_orders.append( ( 4, order.id ) )
        row.update({
            'log'         : json.dumps( log ),
            'sale_orders' : sale_orders,
        })
        _logger.info( json.dumps( log, indent = 4 ) )
        return rec



