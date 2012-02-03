from gnr.app.gnrapp import GnrApp
from gnr.core.gnrbag import Bag


app = GnrApp('moscati_test')
db = app.db
prov = db.table('glbl.provincia')
milano = prov.record(sigla='MI').output('bag')
print milano['@regione.nome']
milano['regione'] = 'PUG'
print milano['@regione.nome']


print 'ok'