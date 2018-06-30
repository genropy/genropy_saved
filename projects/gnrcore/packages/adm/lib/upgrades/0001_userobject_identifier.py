# encoding: utf-8

def main(db):
    print '\t fix identifier in userobject'
    tblobj = db.table('adm.userobject')
    f = tblobj.query(where='$identifier IS NULL',for_update=True,addPkeyColumn=False,order_by='$__ins_ts desc').fetch()
    addedidentifier = set()
    for i,r in enumerate(f):    
        oldrec = dict(r)
        if (r['pkg'] and not db.package(r['pkg'])) or  (r['tbl'] and not db.table(r['tbl'])):
            print 'deleting userobject',r,'because does not exist tbl or package'
            tblobj.delete(r)
        identifier = '%s%s%s' %(r['pkg'] or r['tbl'] or '',r['objtype'],r['code'])
        if identifier in addedidentifier:
            print 'found duplicate for',identifier
            r['code'] = '%s_%i' %(r['code'],i)
            identifier = '%s%s%s' %(r['pkg'] or r['tbl'] or '',r['objtype'],r['code'])
            if r['description']:
                r['description'] = '%s [dup]' %r['description']
        tblobj.update(r,oldrec)
        addedidentifier.add(identifier)
