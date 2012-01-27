from gnr.app.gnrapp import GnrApp
from gnr.core.gnrbag import Bag


app = GnrApp('moscati_test')
db = app.db
prestazione = db.table('polimed.prestazione')
medico_col = prestazione.column('medico')
#cognome_nome = prestazione.column('@medico_id.cognome_nome')
ragione_sociale = prestazione.column('@medico_id.@anagrafica_id.ragione_sociale')

print 'aaa'


print 'ok'