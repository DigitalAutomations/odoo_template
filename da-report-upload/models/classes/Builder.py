######################################

import logging, json
from datetime import datetime

class Builder:
    "A partire dal risultato del self.parser costruisce gli ordini di vendita"

    def __init__( self, parser, models, logger ):
        self.models = models
        self.parser = parser
        self.logger = logger
        self.logs   = []
        self.orders = []

    ## public methods #####################################

    def log( self, msg ):
        self.logger.info( msg )

    def msg( self, msg ):
        self.logs.append( msg )

    ## static methods #####################################

    @classmethod
    def build( cls, parser, models ):
        logger = logging.getLogger(__name__)
        logger.info( '# # # # # # ' )
        obj = cls( parser, models, logger )
        obj.msg('Build degli ordini di vendita')
        try:
            obj._build()
        except Exception as e:
            logger.info( e )
        obj.msg('Build Terminato')
        logger.info( '# # # # # # ' )
        return obj

    ## private mathods ####################################

    def _build(self):
        self._build_order_1()
        self._build_order_2()
        self._build_order_3()
        self._build_order_4()
        self._build_order_5()

    def _build_order_5(self):
        # Hardware
        if len( self.parser.block5['rows'] ) > 0:
            self.msg('Ordine 5')
            # intestazione
            sale_order = self._build_order_header()
            self.orders.append( sale_order )
          

            self.models['sale.order.line'].create({
                'name'            : 'Hardware',
                'order_id'        : sale_order.id,
                'price_unit'      : 0,
                'product_uom_qty' : 0,
                'customer_lead'   : 0,
                'display_type'    : 'line_section',
                'discount'        : 0,
                'company_id'      : 1,
            })
            for ass in self.parser.block5['rows']:
                prod_row = self.models['product.product'].search( [ ( 'default_code', '=', ass['articolo'] ) ] )
                if prod_row:
                    prod_template_row = self.models['product.template'].search( [ ( 'default_code', '=', ass['articolo'] ) ] )
                    if prod_template_row:
                        self.models['sale.order.line'].create({
                            'name'            : '[%s] %s' % ( ass['articolo'], prod_template_row['name'] ),
                            'order_id'        : sale_order.id,
                            'product_id'      : prod_row.id,
                            'price_unit'      : ass['unitario'],
                            'product_uom_qty' : ass['numero_stima'],
                            'customer_lead'   : 0,
                            'discount'        : 0,
                        })
                    else:
                        # messaggio di errore
                        self.log( 'prod template row non trovata' )
                else:
                    # messaggio di errore
                    self.log( 'prod row non trovata' )

    def _build_order_4(self):
        # Assistenza
        if len( self.parser.block4['rows'] ) > 0:
            self.msg('Ordine 4')
            # intestazione
            sale_order = self._build_order_header()
            self.orders.append( sale_order )

            self.models['sale.order.line'].create({
                'name'            : 'Assistenza',
                'order_id'        : sale_order.id,
                'price_unit'      : 0,
                'product_uom_qty' : 0,
                'customer_lead'   : 0,
                'display_type'    : 'line_section',
                'discount'        : 0,
                'company_id'      : 1,
            })
            for ass in self.parser.block4['rows']:
                prod_row = self.models['product.product'].search( [ ( 'default_code', '=', ass['articolo'] ) ] )
                if prod_row:
                    prod_template_row = self.models['product.template'].search( [ ( 'default_code', '=', ass['articolo'] ) ] )
                    if prod_template_row:
                        self.models['sale.order.line'].create({
                            'name'            : '[%s] %s' % ( ass['articolo'], prod_template_row['name'] ),
                            'order_id'        : sale_order.id,
                            'product_id'      : prod_row.id,
                            'price_unit'      : ass['prezzo'],
                            'product_uom_qty' : ass['qta'],
                            'customer_lead'   : 0,
                            'discount'        : ass['sconto'] * 100,
                        })
                    else:
                        # messaggio di errore
                        self.log( 'prod template row non trovata' )
                else:
                    # messaggio di errore
                    self.log( 'prod row non trovata' )

    def _build_order_3(self):
        # Manutenzione
        if len( self.parser.block3['rows'] ) > 0:
            self.msg('Ordine 3')
            # intestazione
            sale_order = self._build_order_header()
            self.orders.append( sale_order )

            self.models['sale.order.line'].create({
                'name'            : 'Manutenzione',
                'order_id'        : sale_order.id,
                'price_unit'      : 0,
                'product_uom_qty' : 0,
                'customer_lead'   : 0,
                'display_type'    : 'line_section',
                'discount'        : 0,
                'company_id'      : 1,
            })
            for ass in self.parser.block3['rows']:
                prod_row = self.models['product.product'].search( [ ( 'default_code', '=', ass['articolo'] ) ] )
                if prod_row:
                    prod_template_row = self.models['product.template'].search( [ ( 'default_code', '=', ass['articolo'] ) ] )
                    if prod_template_row:
                        self.models['sale.order.line'].create({
                            'name'            : '[%s] %s' % ( ass['articolo'], prod_template_row['name'] ),
                            'order_id'        : sale_order.id,
                            'product_id'      : prod_row.id,
                            'price_unit'      : ass['valore'],
                            'product_uom_qty' : ass['qta'],
                            'customer_lead'   : 0,
                            'discount'        : ass['sconto'] * 100,
                        })
                    else:
                        # messaggio di errore
                        self.log( 'prod template row non trovata' )
                else:
                    # messaggio di errore
                    self.log( 'prod row non trovata' )

    def _build_order_2(self):
        # licenze microsoft
        if len( self.parser.block2['rows'] ) > 0:
            self.msg('Ordine 2')
            # intestazione
            sale_order = self._build_order_header()
            self.orders.append( sale_order )

            self.models['sale.order.line'].create({
                'name'            : 'Licenze Microsoft',
                'order_id'        : sale_order.id,
                'price_unit'      : 0,
                'product_uom_qty' : 0,
                'customer_lead'   : 0,
                'display_type'    : 'line_section',
                'discount'        : 0,
                'company_id'      : 1,
            });
        for lic in self.parser.block2['rows']:
            prod_row = self.models['product.product'].search( [ ( 'default_code', '=', lic['articolo'] ) ] )
            if not prod_row:
                continue;
            prod_template_row = self.models['product.template'].search( [ ( 'default_code', '=', lic['articolo'] ) ] )
            if not prod_template_row:
                continue;
            sale_order_line = {
                'name'            : '[%s] %s' % ( lic['articolo'], prod_template_row['name'] ),
                'order_id'        : sale_order.id,
                'product_id'      : prod_row.id,
                'price_unit'      : lic['prezzo'],
                'product_uom_qty' : lic['qta'],
                'customer_lead'   : 0,
                'discount'        : lic['sconto'] * 100,
            }
            self.models['sale.order.line'].create( sale_order_line )

    def _build_order_1(self):
        self.msg('Ordine 1')
        # intestazione
        sale_order = self._build_order_header()
        self.orders.append( sale_order )

        # licenze stesi
        if len( self.parser.block1['licenze']['rows'] ) > 0:
            self.models['sale.order.line'].create({
                'name'            : 'Licenze',
                'order_id'        : sale_order.id,
                'price_unit'      : 0,
                'product_uom_qty' : 0,
                'customer_lead'   : 0,
                'display_type'    : 'line_section',
                'discount'        : 0,
                'company_id'      : 1,
            });
        for lic in self.parser.block1['licenze']['rows']:
            prod_row = self.models['product.product'].search( [ ( 'default_code', '=', lic['articolo'] ) ] )
            if not prod_row:
                continue;
            prod_template_row = self.models['product.template'].search( [ ( 'default_code', '=', lic['articolo'] ) ] )
            if not prod_template_row:
                continue;
            sale_order_line = {
                'name'            : '[%s] %s' % ( lic['articolo'], prod_template_row['name'] ),
                'order_id'        : sale_order.id,
                'product_id'      : prod_row.id,
                'price_unit'      : lic['prezzo'],
                'product_uom_qty' : lic['qta'],
                'customer_lead'   : 0,
                'discount'        : lic['sconto'] * 100,
            }
            self.models['sale.order.line'].create( sale_order_line )

        # manutenzione anticipata
        if len( self.parser.block1['manutenzione_anticipata']['rows'] ) > 0 and self.parser.block1['manutenzione_anticipata']['total']['valore'] > 0:
            self.models['sale.order.line'].create({
                'name'            : 'Servizio Manutenzione Anticipata',
                'order_id'        : sale_order.id,
                'price_unit'      : 0,
                'product_uom_qty' : 0,
                'customer_lead'   : 0,
                'display_type'    : 'line_section',
                'discount'        : 0,
                'company_id'      : 1,
            });
            for lic in self.parser.block1['manutenzione_anticipata']['rows']:
                prod_row = self.models['product.product'].search( [ ( 'default_code', '=', self.parser.block1['manutenzione_anticipata']['total']['articolo'] ) ] )
                if not prod_row:
                    continue;
                prod_template_row = self.models['product.template'].search( [ ( 'default_code', '=', self.parser.block1['manutenzione_anticipata']['total']['articolo'] ) ] )
                if not prod_template_row:
                    continue;
                sale_order_line = {
                    'name'            : '[%s] %s' % ( self.parser.block1['manutenzione_anticipata']['total']['articolo'], prod_template_row['name'] ),
                    'order_id'        : sale_order.id,
                    'product_id'      : prod_row.id,
                    'price_unit'      : lic['prezzo'],
                    'product_uom_qty' : lic['qta'],
                    'customer_lead'   : 0,
                   #'discount'        : lic['sconto'] * 100,
                    'discount'        : 0,
                }
                self.models['sale.order.line'].create( sale_order_line )

        # attivazione
        if len( self.parser.block1['attivazione']['table']['rows'] ) > 0:
            self.models['sale.order.line'].create({
                'name'            : 'Attivazione',
                'order_id'        : sale_order.id,
                'price_unit'      : 0,
                'product_uom_qty' : 0,
                'customer_lead'   : 0,
                'display_type'    : 'line_section',
                'discount'        : 0,
                'company_id'      : 1,
            });
            prod_row = self.models['product.product'].search( [ ( 'default_code', '=', self.parser.block1['attivazione']['table']['total']['articolo'] ) ] )
            if prod_row:
                prod_template_row = self.models['product.template'].search( [ ( 'default_code', '=', self.parser.block1['attivazione']['table']['total']['articolo'] ) ] )
                if prod_template_row:
                    sale_order_line = {
                        'name'            : '[%s] %s' % ( self.parser.block1['attivazione']['table']['total']['articolo'], prod_template_row['name'] ),
                        'order_id'        : sale_order.id,
                        'product_id'      : prod_row.id,
                        'price_unit'      : self.parser.block1['attivazione']['table']['total']['valore'],
                        'product_uom_qty' : 1,
                        'customer_lead'   : 0,
                       #'discount'        : self.parser.block1['attivazione']['sconto'] * 100,
                        'discount'        : 0,
                    }
                    self.models['sale.order.line'].create( sale_order_line )
                else:
                    # messaggio di errore
                    pass
            else:
                # messaggio di errore
                pass

        # spese trasferta
        if 'spese_trasferta' in self.parser.block1.keys() and self.parser.block1['spese_trasferta']['valore'] > 0:
            self.models['sale.order.line'].create({
                'name'            : 'Spese Trasferta',
                'order_id'        : sale_order.id,
                'price_unit'      : 0,
                'product_uom_qty' : 0,
                'customer_lead'   : 0,
                'display_type'    : 'line_section',
                'discount'        : 0,
                'company_id'      : 1,
            })
            prod_row = self.models['product.product'].search( [ ( 'default_code', '=', self.parser.block1['spese_trasferta']['articolo'] ) ] )
            if prod_row:
                prod_template_row = self.models['product.template'].search( [ ( 'default_code', '=', self.parser.block1['spese_trasferta']['articolo'] ) ] )
                if prod_template_row:
                    self.models['sale.order.line'].create({
                        'name'            : '[%s] %s' % ( self.parser.block1['spese_trasferta']['articolo'], prod_template_row['name'] ),
                        'order_id'        : sale_order.id,
                        'product_id'      : prod_row.id,
                        'price_unit'      : self.parser.block1['spese_trasferta']['valore'],
                        'product_uom_qty' : 1,
                        'customer_lead'   : 0,
                        'discount'        : self.parser.block1['spese_trasferta']['sconto'] * 100,
                    })
                else:
                    # messaggio di errore
                    pass
            else:
                # messaggio di errore
                pass

    def _build_order_header(self):
        self.msg('  - header dell\'ordine')
        cliente_diretto = self.models['res.partner'].search( [ ( 'ref', '=', self.parser.header['cod_cliente_diretto'] ) ] )
        sale_order_data = {
            'date_order'          : datetime.today().strftime('%Y-%m-%d %H:%M'),
            'partner_id'          : cliente_diretto.id,
            'partner_invoice_id'  : cliente_diretto.id,
            'partner_shipping_id' : cliente_diretto.id,
            'pricelist_id'        : 1,
            'company_id'          : 1,
            'picking_policy'      : 'direct',
            'warehouse_id'        : 1,
            'title'               : self.parser.header['title'],
            'num_offerta_stesi'   : self.parser.header['num_offerta'],
        }
        cliente_indiretto = None
        if self.parser.header['cod_cliente_indiretto']:
            cliente_indiretto = self.models['res.partner'].search( [ ( 'ref', '=', self.parser.header['cod_cliente_indiretto'] ) ] )
            if cliente_indiretto is not False:
                sale_order_data['indirect_partner_id'] = cliente_indiretto.id
            else:
                self.log('cliente indiretto non trovato')
                self.msg( '  - cliente indiretto non trovato (%s)' % self.parser.header['cod_cliente_indiretto'] )
        sale_order = self.models['sale.order'].create( sale_order_data )
        return sale_order

