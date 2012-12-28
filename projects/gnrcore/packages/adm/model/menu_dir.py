#!/usr/bin/env python
# encoding: utf-8

#from gnr.core.gnrbag import Bag

class Table(object):
    def config_db(self, pkg):
        tbl = pkg.table('menu_dir', pkey='id', name_long='!!Menu Directory',name_plural='!!Menu Directories', rowcaption='$hierarchical_label',caption_field='hierarchical_label')
        self.sysFields(tbl, hierarchical='label',counter=True)
        tbl.column('label', name_long='!!Label')
        tbl.column('tags', name_long='!!Tags')
        tbl.column('summary', name_long='!!Summary')

  # def importFromBag(self, bag):
  #     self.empty()
  #     index = bag.getIndex()
  #     for pathlist, node in index:
  #         record = node.getAttr()
  #         record['position'] = str(bag['.'.join(pathlist[:-1])]._index(pathlist[-1]))
  #         record['code'] = '.'.join(pathlist)
  #         f = record.get('file', '')
  #         if '?' in f:
  #             record['file'], record['parameters'] = f.split('?')
  #         self.insert(record)

    def getMenuBag(self, **kwargs):
        tbl_page_dir = self.db.table('adm.menu_page_dir')
        linked_pages = tbl_page_dir.query(columns='$dir_hierarchical_pkey,$page_label,$page_file,$page_table,$page_metadata').fetchGrouped('dir_hierarchical_pkey')
        if len(linked_pages) is 0:
            return
        tbl_page_dir = self.db.table('adm.menu_dir')
        #menu_dirs = tbl_page_dir.query(where='$id ILI')