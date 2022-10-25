######################################

import logging

from .BaseGroup import BaseGroup

class ManutenzioneAnticipata(BaseGroup):

    "Esegue il parsing del gruppo ManutenzioneAnticipata"

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
            if cells[0].value == '':
                if cells[1].value == '' and cells[2].value == '' and cells[3].value == '' and cells[4].value == '' and cells[5].value == '':
                    continue
                self.table['rows'].append({
                    'modulo' : cells[1].value,
                    'qta'    : cells[2].value,
                    'prezzo' : cells[3].value,
                    'sconto' : cells[4].value,
                    'valore' : cells[5].value,
                })
            else:
                self.table['total'] = {
                    'articolo' : cells[0].value,
                    'modulo'   : cells[1].value,
                    'valore'   : cells[5].value,
                }
                self.msg('totale della manutenzione anticipata estratto con successo')

    def _validate(self):
        pass

