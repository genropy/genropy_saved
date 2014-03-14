from gnr.app.gnrapp import GnrApp
from gnr.core.gnrbag import Bag


app = GnrApp('moscati')
db = app.db
qin = db.table('glbl.provincia').query(columns='$sigla,$nome',where='( $sigla IN :s )',s=['AL','MI','CO','BG','BS','RM'],order_by='$sigla')

#qany = db.table('glbl.provincia').query(columns='$sigla,$nome',where='NOT ( $sigla = ANY(:s) )',s=['AL','MI','CO','BG','BS','RM'],order_by='$sigla')

#event = db.table('base.event')
#qevt = event.query(columns='$id,$inpatient,@estimate_id.inv_total,@estimate_id.inv_total_test')
#print qevt.sqltext
#res = estimate.query(columns='$id,$inv_total_test,$inv_total',limit=1).selection().output('grid')
#q = estimate.query(columns='$id,@service_id.@patient_id.name_full')


print qin.fetch()

