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

    report      = fields.Binary( string = 'Report', required = True )
    file_name   = fields.Char( string = 'File Name', required = False )
    note        = fields.Text( string = 'Note', required = False, default = None )
    log         = fields.Text( string = 'Log', required = False, default = None )
    status      = fields.Char( string = 'Stato', required = True, default = 'uploaded' )
    log         = fields.Text( string = 'log', required = False, default = None )
    sale_orders = fields.Many2many( 'sale.order', 'report_sale_order_rel', 'report_id', 'sale_order_id', string = 'Ordini di vedita' )

    def action_parse_report( self ):
        self.ensure_one()
        row = self.env['da.reports'].search( [ ( 'id', '=', self.id ) ], limit = 1 )
        parser = Parser.parse( self.report, self.env )

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



