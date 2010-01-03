#!/usr/bin/env python
# encoding: utf-8

from gnr.core.gnrbag import Bag

class Table(object):
    def config_db(self, pkg):
        tbl =  pkg.table('menu',  pkey='id', name_long='!!Menu Lines', rowcaption='')
        self.sysFields(tbl, md5=True)
        tbl.column('id',size='22',group='_',readOnly='y',name_long='Id')
        tbl.column('code',name_long='!!Code', required=True, unique=True, indexed=True)
        tbl.column('label', name_long='!!Label')
        tbl.column('basepath',name_long='!!Basepath')
        tbl.column('tags',name_long='!!Tags')
        tbl.column('file',name_long='!!Filename')
        tbl.column('description',name_long='!!Description')
        tbl.column('parameters',name_long='!!Parameters')
        tbl.column('position', name_long='!!Position')
        tbl.column('_class', name_long='!!Class')
        tbl.column('_style', name_long='!!Style')
        tbl.formulaColumn('level',"(length($code)-length(replace($code,'.','')))", name_long='!!Level',dype='L')
        
    def importFromBag(self,bag):
        self.empty()
        index=bag.getIndex()
        for pathlist,node in index:
            record = node.getAttr()
            record['position'] = str(bag['.'.join(pathlist[:-1])]._index(pathlist[-1]))
            record['code'] = '.'.join(pathlist)
            f=record.get('file','')
            if '?' in f:
                    record['file'],record['parameters'] = f.split('?')
            self.insert(record)
    
    def getMenuBag(self, **kwargs):
        lines=self.query(order_by='$level,$position', **kwargs).fetch()
        result=Bag()
        for line in lines:
            result.setItem(line['code'],None,line)
        return result