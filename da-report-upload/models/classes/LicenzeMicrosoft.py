######################################

import logging

from .BaseGroup import BaseGroup

class LicenzeMicrosoft(BaseGroup):

    "Esegue il parsing del gruppo LicenzeMicrosoft"

    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(__name__)

    ## public methods ####################################

    def log( self, msg ):
        self.logger.info( msg )

    def parse(self):
        self._exclude_empty_lines()
        self._table()
        self._spese_trasferta()

    ## private methods ###################################

    def _table(self):
        self.table = { 'rows': [], 'total': {} }
        for cells in self.rows:
            if cells[0].value != 'Sezione' and cells[5].value > 0:
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
            else:
                self.table['total'] = {
                    'valore'   : cells[5].value,
                }
                break
        self.msg('trovate %s righe di licenze microsoft valide' % str( len( self.table['rows'] ) ) )

    def _spese_trasferta(self):
        self.spese_trasferta = {}
        for cells in self.rows:
            if ( cells[1].value == 'Spese Trasferta' ):
                self.spese_trasferta = {
                    'articolo' : cells[0].value,
                    'modulo'   : cells[1].value,
                    'qta'      : cells[2].value,
                    'prezzo'   : cells[3].value,
                    'sconto'   : cells[4].value,
                    'valore'   : cells[5].value,
                    'note'     : None if cells[8].value == '' else cells[8].value,
                }
                self.msg('spese trasferta estratte con successo')
                break

    def _validate(self):
        pass

