from __future__ import print_function
from gnr.core.gnrlist import XlsReader
from gnr.app.gnrapp import GnrApp

def importXlsProvince(db,docname):
    reader = XlsReader(docname)
    prov = db.table('glbl.provincia')
    reg = db.table('glbl.regione')
    regioni_dict = dict()

    for row in reader():
        row = dict(row)
        cod_reg = '%02i' %row['cod_reg']
        if not cod_reg in regioni_dict:
            reg_rec = reg.record(where='$codice_istat=:cod_reg',cod_reg=cod_reg,for_update=True).output('dict')
            oldrec = dict(reg_rec)
            reg_rec['zona_numero'] = row['cod_rip']
            reg_rec['zona'] = row['zona']
            reg_rec['nuts'] = row['nuts2']
            reg_rec['nome'] = row['regione_desc']
            reg.update(reg_rec,oldrec)
            print('oldregione',oldrec,'regione updated' ,reg_rec)
            regioni_dict[cod_reg] = reg_rec
        rec_prov = dict()
        rec_prov['sigla'] = row['prov_sigla']
        rec_prov['codice_istat'] = '%03i' %row['cod_prov']
        rec_prov['nome'] = row['prov_desc']
        rec_prov['nuts'] = row['nuts3']
        rec_prov['regione'] = regioni_dict[cod_reg]['sigla']
        prov.insertOrUpdate(rec_prov)


if __name__ == '__main__':
    db = GnrApp('autosped').db
    d = importXlsProvince(db, '../../../data/province.xls')
    db.commit()
    print('OK')