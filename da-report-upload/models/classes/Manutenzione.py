######################################

import logging

from .BaseGroup import BaseGroup

class Manutenzione(BaseGroup):

    "Esegue il parsing del gruppo Manutenzione"

    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(__name__)

    ## public methods ####################################

    def log( self, msg ):
        self.logger.info( msg )

    def parse(self):
        self._exclude_empty_lines()
        self._table()

    ## private methods ###################################

    def _table(self):
        self.table = { 'rows': [], 'total': {} }
        for cells in self.rows:
            if cells[0].value != '' and cells[5].value > 0:
                obj = {
                    'articolo' : cells[0].value,
                    'modulo'   : cells[1].value,
                    'qta'      : cells[2].value,
                    'prezzo'   : cells[3].value,
                    'sconto'   : cells[4].value,
                    'valore'   : cells[5].value,
                    'note'     : None if cells[8].value == '' else cells[8].value
                }
                self.table['rows'].append( obj )
        self.msg('trovate %s righe di manutenzione valide' % str( len( self.table['rows'] ) ) )

    def _validate(self):
        pass

    def _validate(self):
        pass

