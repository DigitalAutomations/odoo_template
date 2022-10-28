######################################

import logging

from .BaseGroup import BaseGroup

class Licenze(BaseGroup):

    "Esegue il parsing del gruppo Licenze"

    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(__name__)

    ## public methods ####################################

    def log( self, msg ):
        self.logger.info( msg )

    def parse(self):
        self._exclude_empty_lines()
        self._sconto_licenze()
        self._table()

    ## private methods ###################################

    def _sconto_licenze(self):
        for row in self.rows:
             if row[1].value == 'Sconto Licenze':
                 self.sconto = row[4].value
                 self.msg('sconto estratto con successo')

    def _table(self):
        self.table = { 'rows': [], 'total': {} }
        start = False
        for cells in self.rows:
            if ( start == True ):
                if ( cells[0].value != 'Sezione' ):
                    if cells[2].value > 0:
                        obj = {
                            'articolo' : cells[0].value,
                            'modulo'   : cells[1].value,
                            'qta'      : cells[2].value,
                            'prezzo'   : cells[3].value,
                            'sconto'   : cells[4].value,
                            'valore'   : cells[5].value,
                            'listino'  : cells[6].value,
                            'note'     : None if cells[8].value == '' else cells[8].value
                        }
                        self.table['rows'].append( obj )
                else:
                    self.table['total'] = {
                        'valore'   : cells[5].value,
                        'listino'  : cells[6].value,
                    }
            elif cells[0].value == 'Articolo':
                start = True
        self.msg('trovate %s righe di licenze valide' % str( len( self.table['rows'] ) ) )

    def _validate(self):
        pass

