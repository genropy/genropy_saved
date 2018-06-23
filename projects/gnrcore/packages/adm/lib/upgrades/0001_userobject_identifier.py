# encoding: utf-8

def main(db):
    print '\t fix identifier in userobject'
    db.table('adm.userobject').touchRecords(where='$identifier IS NULL')
    
