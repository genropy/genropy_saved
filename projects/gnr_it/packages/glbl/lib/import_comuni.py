from __future__ import print_function
from gnr.core.gnrlist import XlsReader
from gnr.app.gnrapp import GnrApp

def importXlsComuni(db,docname):
    reader = XlsReader(docname)
    comune = db.table('glbl.comune')
    province_dict = db.table('glbl.provincia').query().fetchAsDict('codice_istat')
    print('province',province_dict)
    for row in reader():
        row = dict(row)     
        row['litoraneo'] = True if row['litoraneo'] is 1 else False    
        row['capoluogo'] = True if row['capoluogo'] is 1 else False  
        row['sigla_provincia'] = province_dict[row['codice_provincia']]['sigla']
        comune.insert(row)

if __name__ == '__main__':
    db = GnrApp('autosped').db
    importXlsComuni(db, '../../../data/comuni.xls')
    db.commit()
    print('OK')