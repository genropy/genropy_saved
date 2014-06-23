#!/usr/bin/env python
# encoding: utf-8

from gnr.core.gnrbag import Bag

class Table(object):
    def config_db(self, pkg):
        tbl = pkg.table('menu_page', pkey='id', name_long='!!Menu Page',name_plural='!!Menu Pages', rowcaption='$label',caption_field='label')
        self.sysFields(tbl)
        tbl.column('label', name_long='!!Label')
        tbl.column('filepath', name_long='!!Filepath')
        tbl.column('tbl', name_long='!!Table')
        tbl.column('pkg', name_long='!!Package')
        tbl.column('metadata', name_long='!!Metadata')

    #def importFromBag(self, bag):
    #    self.empty()
    #    index = bag.getIndex()
    #    for pathlist, node in index:
    #        record = node.getAttr()
    #        record['position'] = str(bag['.'.join(pathlist[:-1])]._index(pathlist[-1]))
    #        record['code'] = '.'.join(pathlist)
    #        f = record.get('file', '')
    #        if '?' in f:
    #            record['file'], record['parameters'] = f.split('?')
    #        self.insert(record)
#
    #def getMenuBag(self, **kwargs):
    #    lines = self.query(order_by='$level,$position', **kwargs).fetch()
    #    result = Bag()
    #    for line in lines:
    #        result.setItem(line['code'], None, line)
    #    return result#


