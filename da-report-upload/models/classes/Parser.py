######################################

import logging, json, datetime
import base64, io
from xlrd import open_workbook

from .Licenze                import Licenze
from .ManutenzioneAnticipata import ManutenzioneAnticipata
from .Attivazione            import Attivazione
from .LicenzeMicrosoft       import LicenzeMicrosoft
from .Assistenza             import Assistenza
from .Manutenzione           import Manutenzione
from .Hardware               import Hardware

class Parser:
    "Esegue il parsing di un report di Stesi"

    def __init__( self, report, models, logger ):
        self.models = models
        self.report = report
        self.logger = logger
        self.groups = {}
        self.logs   = []

    ## public methods ####################################

    def log( self, msg ):
        self.logger.info( msg )

    def msg( self, msg ):
        self.logs.append( msg )

    ## static methods ####################################

    @classmethod
    def parse( cls, report, models ):
        logger = logging.getLogger(__name__)
        logger.info( '# # # # # # ' )
        obj = cls( report, models, logger )
        try:
            obj.msg('Parsing del file excel')
            obj._parse()
            obj.msg('Parsing terminato')
        except Exception as e:
            logger.info( e )
            logger.info( json.dumps( obj.logs, indent = 4 ) )
        logger.info( '# # # # # # ' )
        return obj

    ## private methods ###################################

    def _parse(self):
        self._sheets()
        self._header()
        self._groups()
        self._hardware()

    def _hardware(self):
        self.msg( 'Parsing del gruppo HARDWARE:' )
        self.groups['HARDWARE'] = Hardware.parse( self.sheets[2] )
        self.logs += self.groups['HARDWARE'].logs
        
    def _groups(self):
        titles = [ 'LICENZE', 'MANUTENZIONE ANTICIPATA', 'ATTIVAZIONE', 'LICENZE MICROSOFT', 'ASSISTENZA', 'MANUTENZIONE' ]
        sheet = self.sheets[0]
        active_group = None
        active_obj   = None
        for i in range( 6, sheet.nrows ):
            value = sheet.cell( i, 1 ).value
            if value in titles:
                if active_group is not None:
                    self.groups[ active_group ] = active_obj
                    self.msg( 'Parsing del gruppo %s:' % active_group )
                    self.groups[ active_group ].parse()
                    self.logs += self.groups[ active_group ].logs
                active_group = value
                if value == 'LICENZE':
                    active_obj = Licenze()
                elif value == 'MANUTENZIONE ANTICIPATA':
                    active_obj = ManutenzioneAnticipata()
                elif value == 'ATTIVAZIONE':
                    active_obj = Attivazione()
                elif value == 'LICENZE MICROSOFT':
                    active_obj = LicenzeMicrosoft()
                elif value == 'ASSISTENZA':
                    active_obj = Assistenza()
                elif value == 'MANUTENZIONE':
                    active_obj = Manutenzione()
                else:
                    active_obj = None
            else:
                if active_obj is None:
                    continue;
                active_obj.add_row( sheet.row( i ) )
        self.groups[ active_group ] = active_obj
        self.msg( 'Parsing del gruppo %s:' % active_group )
        self.groups[ active_group ].parse()
        self.logs += self.groups[ active_group ].logs

    def _header(self):
        sheet = self.sheets[0]
        self.cod_cliente_diretto   = sheet.cell( 0, 2 ).value
        self.cod_cliente_indiretto = sheet.cell( 1, 2 ).value
        self.num_offerta           = sheet.cell( 2, 2 ).value
        self.title                 = sheet.cell( 4, 1 ).value
        self.msg('Dati di intestazione estratti con successo')

    def _sheets(self):
        inputx = io.BytesIO()
        to_write = base64.decodebytes( self.report )
        inputx.write( to_write )
        book = open_workbook(file_contents=inputx.getvalue())
        self.sheets = book.sheets()
        self.msg( str( len( self.sheets ) ) + ' sheets trovati' )


    ## getters & setters #################################

    def get_header(self):
        return {
            'cod_cliente_diretto'   : self.cod_cliente_diretto,
            'cod_cliente_indiretto' : self.cod_cliente_indiretto,
            'num_offerta'           : self.num_offerta,
            'title'                 : self.title,
        }

    def get_block1(self):
        return {
            'licenze'                 : self.groups['LICENZE'].table,
            'manutenzione_anticipata' : self.groups['MANUTENZIONE ANTICIPATA'].table,
            'spese_trasferta'         : self.groups['LICENZE MICROSOFT'].spese_trasferta,
            'attivazione'             : {
                'sconto' : self.groups['ATTIVAZIONE'].sconto,
                'table'  : self.groups['ATTIVAZIONE'].table,
            }
        }
        

    def get_block2(self):
        return self.groups['LICENZE MICROSOFT'].table

    def get_block3(self):
        return self.groups['MANUTENZIONE'].table

    def get_block4(self):
        return self.groups['ASSISTENZA'].table

    def get_block5(self):
        return self.groups['HARDWARE'].table

    header = property( get_header )
    block1 = property( get_block1 )
    block2 = property( get_block2 )
    block3 = property( get_block3 )
    block4 = property( get_block4 )
    block5 = property( get_block5 )

