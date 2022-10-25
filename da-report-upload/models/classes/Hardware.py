######################################

import logging

from .BaseGroup import BaseGroup

class Hardware(BaseGroup):

    "Esegue il parsing dello sheet Hardware"

    def __init__(self, sheet):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        for i in range( 0, sheet.nrows ):
            self.add_row( sheet.row( i ) )

    ## public methods ####################################

    def log( self, msg ):
        self.logger.info( msg )

    ## static methods ####################################

    @classmethod
    def parse(cls, sheet):
        obj = cls( sheet )
        obj._parse()
        return obj

    ## private methods ###################################

    def _parse(self):
        self._exclude_empty_lines()
        self._table()

    def _table(self):
        self.table = { 'rows': [], 'total': {} }
        for cells in self.rows:
            if ( cells[0].value != '' and cells[0].value != 'Sezione' and cells[0].value != 'Articolo' ) or cells[1].value == 'Servizi Toyota':
                if cells[3].value == 0:
                    continue
                obj = {
                    'articolo'     : cells[0].value,
                    'descrizione'  : cells[1].value,
                    'numero_stima' : cells[3].value,
                    'unitario'     : cells[5].value,
                    'totale_uf'    : cells[6].value,
                }
                self.table['rows'].append( obj )
            elif cells[0].value == 'Sezione':
                self.table['total'] =  cells[6].value
                break
        self.msg('trovate %s righe di hardware valide' % str( len( self.table['rows'] ) ) )

    def _validate(self):
        pass

