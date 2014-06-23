#!/usr/bin/env python
# encoding: utf-8

class Table(object):
    def config_db(self, pkg):
        tbl = pkg.table('nuts', pkey='id', name_long='!!Nomeclatura statistica', 
                name_plural='!!Nomenclatura statistica',
                caption_field='description',rowcaption='$code,$description')
        self.sysFields(tbl,hierarchical=True)
        tbl.column('code' ,name_long='!!Code')
        tbl.column('description' ,name_long='!!Description',name_short='Label')
        tbl.column('level',dtype='I',name_long='!!Level')
        tbl.column('country',size='2',name_long='!!Country')
        tbl.column('country_iso',size='2',name_long='!!Country').relation('glbl.nazione.code',relation_name='nuts',mode='foreignkey',onDelete='raise',deferred=True)

   #def setParent(self):
   #    f = nuts.query(order_by='$code',for_update=True,addPkeyColumn=False).fetch()
   #    for r in f:
   #        code = r['code']
   #        for p in parentDict
   #
    def setParent(self):
        f = self.query(order_by='$code',for_update=True,addPkeyColumn=False).fetch()
        prev_list = []
        for r in f:
            hasparent = False
            for parent_rec in prev_list:
                if r['code'].startswith(parent_rec['code']):
                    oldrecord = dict(r)
                    r['parent_id'] = parent_rec['id']
                    self.update(r,oldrecord)
                    hasparent = True
                    break
            if hasparent:
                prev_list = [r]+prev_list
            else:
                prev_list = [r]

if __name__ == '__main__':
    from gnr.app.gnrapp import GnrApp
    db = GnrApp('autosped').db
    nuts = db.table('glbl.nuts')
    nuts.setParent()
    db.commit()
    
   #f = nuts.query(order_by='code',for_update=True,addPkeyColumn=False).fetch()
   #prev_list = []
   #for r in f:
   #    if prev_listr['code'].startswith(prev_code):
   #        oldrecord = dict(r)
   #        r['parent_id'] = prev_rec['id']
   #        nuts.update(r,oldrecord)
   #    elif len(r):
   #        prev_rec = r
   #        prev_code = r['code']
   #db.commit()
   #print 'OK'