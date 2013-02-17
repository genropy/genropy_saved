from gnr.app.gnrapp import GnrApp
from gnr.core.gnrbag import Bag
from gnr.core.gnrstring import templateReplace


app = GnrApp('gm_moscati')
db = app.db
medico = db.table('gm_base.medico')
vc = medico.model.virtual_columns

print vc
