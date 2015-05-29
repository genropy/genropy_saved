__author__ = 'fporcari'
from gnr.app.gnrapp import GnrApp
db = GnrApp('erpy_softwell').db

for tname,tblobj in db.packages['erpy_coge'].tables.items():
    print tname
    t = tblobj.dbtable
    for m in dir(t):
        if m.startswith('sysRecord_') and m!='sysRecord_':
            print tname,m[10:]
            t.sysRecord(m[10:])
db.commit()
print 'fatto'