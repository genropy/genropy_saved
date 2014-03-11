from gnr.app.gnrapp import GnrApp
from gnr.core.gnrbag import Bag


app = GnrApp('icond')
db = app.db
q = db.table('cond.nu_nominativo').query(columns='$id,@stato_id.sum_quota_possesso',limit=1,_storename='rela_1')

#event = db.table('base.event')
#qevt = event.query(columns='$id,$inpatient,@estimate_id.inv_total,@estimate_id.inv_total_test')
#print qevt.sqltext
#res = estimate.query(columns='$id,$inv_total_test,$inv_total',limit=1).selection().output('grid')
#q = estimate.query(columns='$id,@service_id.@patient_id.name_full')

tt = q.sqltext
print tt

