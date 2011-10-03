#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#
#  untitled
#
#  Created by Giovanni Porcari on 2007-03-24.
#  Copyright (c) 2007 Softwell. All rights reserved.
#
# --------------------------- GnrWebPage subclass ---------------------------
from gnr.web.gnrwebpage import GnrGenshiPage as page_factory
from gnr.web.gnrwsgisite import httpexceptions



class GnrCustomWebPage(object):
    from tools import codeToPath
    css_requires='website'
    
    def _pageAuthTags(self, method=None, **kwargs):
           return 'user'
    
    def genshi_template(self):
        return 'websiteResourceDispatcher.html'
    
    def main(self, rootBC, **kwargs):
        pass

    def getWebResource(self):
        preview=False
        folder_tbl=self.db.table('website.folder')
        page_tbl=self.db.table('website.page')
        resource_path=self._call_args
        resource_permalink = resource_path[-1]
        if len(resource_path)>=1:
            if resource_path[0]=='preview':
                preview=True
                resource_path=resource_path[1:]
        if '.' in resource_permalink:
            resource_permalink=resource_permalink.split('.')[0]
        code='.'.join(resource_path)
        folder=folder_tbl.query(where='$code=:code',code=code).fetch()
        if folder:
            return dict(page=self.getIndex(folder[0],preview=preview),folder=folder[0],path=self.codeToPath(folder[0]))
        else:
            code='.'.join(resource_path[:-1])
            folder=folder_tbl.query(where='$code=:code',code=code).fetch()
            if folder:
                where='$folder=:folder_pkey AND $permalink=:resource_permalink AND $publish>=:date'
                if preview:
                    where='$folder=:folder_pkey AND $permalink=:resource_permalink'
                page=page_tbl.query(where=where,
                                    folder_pkey=folder[0]['pkey'],
                                    resource_permalink=resource_permalink,date=self.workdate).fetch()
                if page:
                    return dict(page=page[0],folder=folder[0],path=self.codeToPath(folder[0]))
        raise httpexceptions.HTTPNotFound(comment='Page not found.')

    def getMenu(self):
        menu=list()
        folders=mainpage.db.table('website.folder').query(where='level=:livello',livello='0',order_by='$position asc').fetch()
        for f in folders:
            subfolders=folders=mainpage.db.table('website.folder').query(where='parent_code=:padre',padre=f['code']).fetch()
            menu.append([f,subfolders])
        return menu

    def getPagesByFolder(self,folder):
        return self.db.table('website.page').query(where='$folder=:folder_pkey AND $publish>=:date',date=self.workdate,folder_pkey=folder['pkey'],order_by='position').fetch()

    def getSubFoldersByFolder(self,folder):
        return self.db.table('website.folder').query(where='$parent_code=:code',code=folder['code'],order_by='$position asc').fetch()

    def getBrothers(self,parentFolder,folder):
        return self.db.table('website.folder').query(where='$parent_code=:code AND $child_code!=:child_code',code=parentFolder['code'],child_code=folder['child_code'],order_by='$position asc').fetch()

    def getFolderByCode(self,code):
        return self.db.table('website.folder').query(where='$code=:code',code=code).fetch()
    def getFolders(self,exclude=None):
        #exclude da implementare esclusione folder dinamici
        return mainpage.db.table('website.folder').query().fetch()
        
    def getIndex(self,folder,preview=False):
        where='$folder=:folder_pkey AND $permalink=:permalink AND $publish>=:date'
        if preview:
            where='$folder=:folder_pkey AND $permalink=:permalink'
        pages=self.db.table('website.page').query(where=where,folder_pkey=folder['pkey'],permalink='index',date=self.workdate).fetch()
        if not pages:
            where='$folder=:folder_pkey AND $publish>=:date'
            if preview:
                where='$folder=:folder_pkey'
            pages=self.db.table('website.page').query(where=where,folder_pkey=folder['pkey'],date=self.workdate,order_by='position').fetch()
        if pages:
            return pages[0] 
        return []