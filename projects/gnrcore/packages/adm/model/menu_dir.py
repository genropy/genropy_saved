#!/usr/bin/env python
# encoding: utf-8

#from gnr.core.gnrbag import Bag
from gnr.core.gnrdecorator import public_method
from gnr.core.gnrbag import Bag
from gnr.core.gnrstring import stringDict,asDict
from datetime import datetime
import os

class Table(object):
    def config_db(self, pkg):
        tbl = pkg.table('menu_dir', pkey='id', name_long='!!Menu Directory',name_plural='!!Menu Directories', rowcaption='$hierarchical_label',caption_field='hierarchical_label')
        self.sysFields(tbl, hierarchical='label',counter=True)
        tbl.column('label', name_long='!!Label')
        tbl.column('tags', name_long='!!Tags')
        tbl.column('summary', name_long='!!Summary')
        tbl.column('ts_import',dtype='DH')

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
        linked_pages = tbl_page_dir.query(columns='$dir_hierarchical_pkey,$page_label,$page_filepath,$page_tbl,$page_metadata').fetchGrouped('dir_hierarchical_pkey')
        if len(linked_pages) is 0:
            return
        tbl_page_dir = self.db.table('adm.menu_dir')
        #menu_dirs = tbl_page_dir.query(where='$id ILI')

    def rootId(self):
        return '_ROOT_'.ljust(22,'_')

    def pkgId(self,pkgId):
        return ('_ROOT_%s_' %pkgId).ljust(22,'_')

    @public_method
    def createRootHierarchy(self):
        root_id=self.rootId()
        root = self.query(where='$id=:root_id',root_id=root_id).fetch()
        if not root:
            root = dict(id=root_id,label='Menu Root',parent_id=None)
            self.insert(root)
        packages = self.db.application.packages
        packages_dir = self.query(where='$parent_id=:root_id',root_id=root_id).fetchAsDict('id')
        for pkgId,pkg in packages.items():
            menupath = os.path.join(pkg.packageFolder, 'menu.xml')
            if not os.path.exists(menupath):
                continue
            ts = os.path.getmtime(menupath)
            ts = datetime.fromtimestamp(ts)
            pkg_pkey =  self.pkgId(pkgId)
            if pkg_pkey in packages_dir and  packages_dir[pkg_pkey]['ts_import'] == ts:
                continue
            pkgrec = packages_dir.get(pkg_pkey)
            if not pkgrec:
                pkgattr = pkg.attributes
                pkgrec = dict(label=pkgattr['name_long'].replace('!!',''),id=pkg_pkey,parent_id=root_id,ts_import=ts)
                self.insert(pkgrec)
            else:
                olderc = dict(pkgrec)
                pkgrec['ts_import'] = ts
                self.update(pkgrec,olderc)
            self.updatePackageHierarchy(Bag(menupath),dir_id=pkg_pkey,pkgId=pkgId)
        self.db.commit()

            
    def updatePackageHierarchy(self,menu,dir_id=None,currpath=None,pkgId=None):
        currpath = currpath or []
        tblpage = self.db.table('adm.menu_page')
        tbllink = self.db.table('adm.menu_page_dir')
        allpackages = self.db.application.packages.keys()
        for node in menu:
            attr = node.attr
            tbl = attr.pop('table',None)
            filepath = attr.get('file',None)
            label = attr.get('label',None)
            label = label.replace('!!','') if label else node.label
            tags = attr.get('tags',None)
            if tbl or filepath:
                page_rec = dict(metadata=stringDict(attr) if attr else None)
                if tbl:
                    page_rec['pkg'] = tbl.split('.')[0]
                    page_rec['tbl'] = tbl
                elif filepath:
                    filepath = currpath+filepath.strip('/').split('/')
                    if not filepath[0] in allpackages:
                        filepath.insert(0,pkgId)
                    page_rec['pkg'] = filepath[0]
                    page_rec['filepath'] ='/%s' %'/'.join(filepath)
                if not tblpage.checkDuplicate(**page_rec):
                    label = label
                    page_rec['label'] = label
                    tblpage.insert(page_rec)
                    tbllink.insert(dict(page_id=page_rec['id'],tags=tags,label=label,dir_id=dir_id))
            elif isinstance(node.value,Bag):
                basepath = attr.get('basepath')
                new_dir_rec = dict(label=label,tags=tags,parent_id=dir_id)
                dir_rec = self.record(ignoreMissing=True,**new_dir_rec).output('dict') or new_dir_rec
                if not dir_rec.get('id'):
                    self.insert(dir_rec)
                self.updatePackageHierarchy(node.value,dir_id = dir_rec['id']
                                             ,currpath=currpath+basepath.strip('/').split('/') if basepath else currpath,pkgId=pkgId)



        