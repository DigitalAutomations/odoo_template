######################################

class BaseGroup:

    "Parent per la gesione dei gruppi di dati dei file excel"

    def __init__(self):
        self.rows = []
        self.logs = []

    ## public methods ####################################

    def add_row(self, row):
        self.rows.append( row )

    def msg( self, msg ):
        self.logs.append( '  - ' + msg )

    ## private methods ###################################

    def _exclude_empty_lines(self):
        rows = []
        for row in self.rows:
            if not self._is_empty( row ):
                rows.append( row )
        self.msg( 'escluse %s righe vuote' % str( len( self.rows ) - len( rows ) ) )
        self.rows = rows

    def _is_empty(self, row):
        is_empty = True
        for cell in row:
            if cell.value != '':
                is_empty = False
                break
        return is_empty

