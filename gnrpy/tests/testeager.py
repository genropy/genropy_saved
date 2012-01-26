from gnr.app.gnrapp import GnrApp
from gnr.core.gnrbag import Bag


app = GnrApp('moscati_test')
db = app.db
tbl = db.table('test15.nodetbl').relationExplorer()
print 'ok'