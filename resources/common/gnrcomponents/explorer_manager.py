# -*- coding: UTF-8 -*-

# untitled.py
# Created by Francesco Porcari on 2010-11-13.
# Copyright (c) 2010 Softwell. All rights reserved.

from gnr.web.gnrbaseclasses import BaseComponent
from gnr.core.gnrbag import DirectoryResolver

class ExplorerManager(BaseComponent):
    py_requires ='gnrcomponents/htablehandler:HTableHandlerBase'
    def onMain_explorer_manager(self):
        explorers = getattr(self,'explorers',None)
        if explorers:
            self.expmng_main(explorers)
    
    def expmng_draggable_types(self):
        return ','.join(['%s_item' %n.split('_',1)[1] for n in dir(self) if n.startswith('onDroppedItem_')])
       
    def expmng_main(self,explorers):
        explorer_to_create = explorers.split(',')
        pane = self.pageSource('pbl_bottomBarCenter').value
        pane.dock(id='explorer_dock',width='100px',background='none',border=0,float='right')
        floating = pane.floatingPane(title='!!Explorers',height='400px',width='300px',
                        top='100px',right='100px',closable=False,resizable=True,persist=True,
                        dockable=True,dockTo='explorer_dock',_class='shadow_4',visibility='hidden',
                        datapath='gnr.explorers')
        tc = floating.tabContainer(margin='2px')
                        
        for explorer_name in explorer_to_create:
            explorer_pars=None
            if ':' in explorer_name:
                explorer_name,explorer_pars=explorer_name.split(':')
            handler= getattr(self,'explorer_'+explorer_name,None)
            pane=tc.contentPane(title=explorer_name,datapath='.%s' %explorer_name.replace('.','_'))
            if handler:
                handler(pane,explorer_pars)
            else:
                self.expmng_htableExplorer(pane,explorer_table=explorer_name,rootpath=explorer_pars)
        
    
    def expmng_htableExplorer(self,pane,explorer_table=None,rootpath=None):
        tblobj = self.db.table(explorer_table)
        title=tblobj.name
        pane.attributes['title'] = title
        related_field = None
        related_table = None
        if '@' in explorer_table:
            pkg,related_table,related_field = explorer_table.split('.')
            related_table = '%s.%s' %(pkg,related_table)
            related_table_obj = self.db.table(related_table)
            explorer_table = related_table_obj.column(related_field).parent.fullname
        data = self.ht_treeDataStore(table=explorer_table,
                                                related_table=related_table,
                                                relation_path=related_field,
                                                rootpath=rootpath,rootcaption=tblobj.name_plural)
        self.expmng_make_explorer(pane,data,explorer_code=explorer_table.replace('.','_'))        
                
    def expmng_make_explorer(self,pane,data,explorer_code=None):
        pane.data('.data',data)
        pane.tree(storepath='.data',
                labelAttribute='caption',
                 _class='fieldsTree',
                 hideValues=True,
                 margin='6px',
                 font_size='.9em',
                 draggable=True,
                 onDrag=""" if(treeItem.attr.child_count && treeItem.attr.child_count>0){
                                return false;
                            }
                            dragValues['text/plain']=treeItem.attr.caption;
                           dragValues['explorer_%s']=treeItem.attr;""" %explorer_code)
                           
    def explorer_directory(self,pane,path=None):
        path = path or '/'
        pane.attributes['title'] = 'Directory:"%s"'%path
        self.expmng_make_explorer(pane,DirectoryResolver(path)(),explorer_code='directory')
        