from gnr.app.gnrapp import GnrApp
from gnr.core.gnrbag import Bag


app = GnrApp('western')
db = app.db
estimate = db.table('base.estimate')
#q = estimate.query(columns='$id,$inv_total_test,$inv_total')
q = estimate.query(columns='$id,@service_id.@patient_id.name_full')
t = q.sqltext
print t


