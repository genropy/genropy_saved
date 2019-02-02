from __future__ import print_function
from gnr.core.gnrlist import XlsReader
from gnr.app.gnrapp import GnrApp

def importXlsNuts(db,docname):
    reader = XlsReader(docname)
    nuts = db.table('glbl.nuts')

    for row in reader():
        rec = dict()
        row = dict(row)
        rec['code'] = row['code']
        rec['description'] = row['description']
        rec['level'] = row['level']
        rec['country'] = row['country']
        rec['country_iso'] = row['country']
        if rec['country_iso'] == 'EL':
            rec['country_iso'] = 'GR'
        if rec['country_iso'] == 'UK':
            rec['country_iso'] = 'GB'            
        nuts.insert(rec)

if __name__ == '__main__':
    db = GnrApp('autosped').db
    d = importXlsNuts(db, '../../../data/nuts.xls')
    db.commit()
    print('OK')