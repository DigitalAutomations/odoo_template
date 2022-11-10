######################################

import logging, json

from .BaseGroup import BaseGroup

class Attivazione(BaseGroup):

    "Esegue il parsing del gruppo Attivazione"

    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(__name__)

    ## public methods ####################################

    def log( self, msg ):
        self.logger.info( msg )

    def parse(self):
        self._exclude_empty_lines()
        self._sconto_servzi()
        self._table()

    ## private methods ###################################

    def _sconto_servzi(self):
        for row in self.rows:
             if row[1].value == 'Sconto Servizi':
                 self.sconto = row[4].value
                 self.msg('sconto estratto con successo')

    def _table(self):
        self.table = { 'rows': [], 'total': {} }
        start = False
        for cells in self.rows:
            if ( start == True ):
                if cells[0].value == '':
                    if cells[2].value > 0:
                        obj = {
                            'modulo'  : cells[1].value,
                            'GG comm' : cells[2].value,
                            'prezzo'  : cells[3].value,
                            'sconto'  : cells[4].value,
                            'valore'  : cells[5].value,
                            'peso'    : cells[6].value,
                            'GG Tec'  : cells[7].value,
                            'note'    : None if cells[8].value == '' else cells[8].value,
                        }
                        self.table['rows'].append( obj )
                else:
                    self.table['total'] = {
                        'articolo' : cells[0].value,
                        'modulo'   : cells[1].value,
                        'valore'   : cells[5].value,
                    }
                    self.msg('totale attivazione estratto con successo')
            elif 'GG Comm' in cells[2].value and cells[6].value == 'Peso' and cells[7].value == 'GG Tec':
                 start = True

    def _validate(self):
        pass

