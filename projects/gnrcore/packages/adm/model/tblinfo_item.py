#!/usr/bin/env python
# encoding: utf-8
from builtins import object
from gnr.core.gnrdecorator import public_method
from gnr.core.gnrbag import Bag
class Table(object):
    def config_db(self, pkg):
        tbl = pkg.table('tblinfo_item',pkey='info_key', pkey_columns='tblid,item_type,code', 
                        name_long='!!Tblinfo item',pkey_columns_joiner='/',
                         name_plural='!!Tblinfo items',caption_field='description')
        self.sysFields(tbl,id=False)
        tbl.column('info_key', size=':50', 
                    readOnly='y', 
                    name_long='!!Info key', 
                    indexed='y',_sysfield=True)
        tbl.column('code' ,size=':30',name_long='!!Code',_sysfield=True)
        tbl.column('description' ,size=':30',name_long='!!Description',_sysfield=True)
        tbl.column('item_type' ,size=':5',name_long='!!Type',values=self.itemTypeValues())
        tbl.column('data',dtype='X',name_long='!!Data',_sendback=True)
        tbl.column('tblid',size=':50').relation('tblinfo.tblid',relation_name='items',mode='foreignkey',onDelete='cascade')

    def itemTypeValues(self):
        return "QTREE:Quick tree,FTREE:Full tree"

    def getInfoItem(self,item_type=None,tbl=None,code=None):
        f = self.query(where='$item_type=:it AND $tblid=:tbl',
                        it=item_type,tbl=tbl,bagFields=True).fetchAsDict('code')
        if code in f:
            return f[code]
        types = self.db.table('adm.user_config').getTypeList(item_type)
        tl = [c for c,d in types if c!='_RAW_']
        if code not in tl:
            return
        tl = tl[:tl.index(code)]
        tl.reverse()
        for c in tl:
            if c in f:
                return f[c]

    @public_method
    def getFilteredOptions(self,_querystring=None,_id=None,tbl=None,item_type=None,**kwargs):
        result = Bag()
        standard_codes = self.db.table('adm.user_config').getTypeList(item_type)
        d = dict(standard_codes)
        codes_to_remove = []
        if tbl:
            codes_to_remove = self.db.table('adm.tblinfo_item').query(where='$tblid=:t AND $item_type=:it AND $code IN :c',
                                        t=tbl,it=item_type,c=list(d.keys()),columns='$code,$description').fetchAsDict('code')
            
        standard_codes = [c for c in standard_codes if not c[0] in codes_to_remove]
        d = dict(standard_codes)
        if _id:
            f = [(_id,d.get(_id))]
        else:
            chunk = _querystring.replace('*','').lower()

            f = [c for c in standard_codes if (chunk in c[1].lower() or chunk in c[0].lower())]
        for i,r in enumerate(f):
            result.setItem('%s_%s' %(r[0],i),None,
               code=r[0],description=r[1],_pkey=r[0],caption=r[1])
        return result,dict(columns='code,description',headers='Code,Description')



    def newRecordCaption(self,record=None):
        return record['description']