from gnr.app.gnrapp import GnrApp
from gnr.core.gnrbag import Bag


app = GnrApp('spc')
db = app.db
tbl = db.table('base.client')
rec = tbl.record(pkey='-lWivnI5PwC9K-LAXoXgiA',virtual_columns='$name_first,$name_last')
b = rec.output('bag')
print b
print 'ok'