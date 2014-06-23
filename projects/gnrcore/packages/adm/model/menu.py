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
        tbl = pkg.table('menu', pkey='id', name_long='!!Menu Directory',name_plural='!!Menu Directories', rowcaption='$hierarchical_label',caption_field='hierarchical_label')
        self.sysFields(tbl, hierarchical='label',counter=True)
        tbl.column('label', name_long='!!Label')
        tbl.column('tags', name_long='!!Tags')
        tbl.column('summary', name_long='!!Summary')
        tbl.column('ts_import',dtype='DH')
        tbl.column('page_id').relation('menu_page.id',mode='foreignkey',relation_name='links')
        tbl.aliasColumn('page_label',relation_path='@page_id.label')
        tbl.aliasColumn('page_filepath',relation_path='@page_id.filepath')
        tbl.aliasColumn('page_tbl',relation_path='@page_id.tbl')
        tbl.aliasColumn('page_metadata',relation_path='@page_id.metadata')

    def rootId(self):
        return '_ROOT_'.ljust(22,'_')

    def pkgId(self,pkgId):
        return ('_ROOT_%s_' %pkgId).ljust(22,'_')

    def getMenuBag(self,root_id=None,userTags=None):
        root_id = root_id or self.rootId()
        q = self.query(where="$hierarchical_pkey LIKE :root_id || '/%%' " ,
                        root_id=root_id,columns='*,$hlevel,$page_label,$page_filepath,$page_tbl,$page_metadata',
                        order_by='$_h_count')

        f = q.fetch()
        if not f:
            return
        result = Bag()
        app = self.db.application
        forbidden = []
        for r in f:
            if userTags is True or (app.checkResourcePermission(r['tags'], userTags) and not r['parent_id'] in forbidden):
                kw = dict()      
                r = dict(r)   
                if r['page_id']:       
                    kw['table'] = r.pop('page_tbl',None)
                    kw['file'] = r.pop('page_filepath',None)
                    if r['page_metadata']:
                        kw.update(asDict(r['page_metadata']))
                        labelClass = 'menu_shape menu_page'
                else:
                    kw['isDir'] = True
                    labelClass='menu_shape menu_level_%i' %(r['hlevel']-2)
                result.setItem(r['hierarchical_pkey'].split('/')[1:],None,label=r['label'],tags=r['tags'], labelClass=labelClass,
                                **kw)  
            else:
                forbidden.append(r['id'])
        empty = True

        while empty:
            empty = False
            for pathlist,n in result.getIndex():
                if n.attr.get('isDir') and  ( (n.value is None) or not n.value):
                    result.popNode(pathlist)
                    empty = True
        return result

    @public_method
    def exportMenu(self,name=None):
        name = name or 'menucustom'
        name = '%s.xml' %name
        site = self.db.application.site
        path = site.getStaticPath('site:exported_menu',name,autocreate=-1)
        self.getMenuBag(userTags=True).toXml(filename=path)
        return site.getStaticUrl('site:exported_menu',name)


    @public_method
    def createRootHierarchy(self,pagesOnly=False):
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
                pkglabel = pkgattr.get('name_long') or pkgId
                pkglabel = pkglabel.replace('!!','')
                pkgrec = dict(label=pkglabel,id=pkg_pkey,parent_id=root_id,ts_import=ts)
                if not pagesOnly:
                    self.insert(pkgrec)
            else:
                olderc = dict(pkgrec)
                pkgrec['ts_import'] = ts
                if not pagesOnly:
                    self.update(pkgrec,olderc)
            self.updatePackageHierarchy(Bag(menupath),dir_id=pkg_pkey,pkgId=pkgId,pagesOnly=pagesOnly)
        self.db.commit()

    def updatePackageHierarchy(self,menu,dir_id=None,currpath=None,pkgId=None,pagesOnly=None):
        currpath = currpath or []
        tblpage = self.db.table('adm.menu_page')
        allpackages = self.db.application.packages.keys()
        for node in menu:
            attr = node.attr
            tbl = attr.pop('table',None)
            filepath = attr.pop('file',None)
            label = attr.pop('label',None)
            label = label.replace('!!','') if label else node.label
            tags = attr.pop('tags',None)
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
                    if not pagesOnly:
                        self.insert(dict(page_id=page_rec['id'],tags=tags,label=label,parent_id=dir_id))
            elif isinstance(node.value,Bag):
                basepath = attr.get('basepath')
                if not pagesOnly:
                    new_dir_rec = dict(label=label,tags=tags,parent_id=dir_id)
                    dir_rec = self.record(ignoreMissing=True,**new_dir_rec).output('dict') or new_dir_rec
                    if not dir_rec.get('id'):
                        self.insert(dir_rec)

                    self.updatePackageHierarchy(node.value,dir_id = dir_rec['id']
                                             ,currpath=currpath+basepath.strip('/').split('/') if basepath else currpath,pkgId=pkgId,pagesOnly=pagesOnly)



        