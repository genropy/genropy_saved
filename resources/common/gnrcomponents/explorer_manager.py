# -*- coding: UTF-8 -*-

# untitled.py
# Created by Francesco Porcari on 2010-11-13.
# Copyright (c) 2010 Softwell. All rights reserved.

from gnr.web.gnrbaseclasses import BaseComponent
from gnr.core.gnrstring import splitAndStrip,fromJson
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
        explorer_to_create = splitAndStrip(explorers,',')
        pane = self.pageSource()
        floating = pane.floatingPane(title='!!Explorers',height='400px',width='300px',
                        top='100px',right='100px',closable=False,resizable=True,persist=True,
                        nodeId='gnr_explorer_floating',
                        dockable=True,dockTo='pbl_dock',_class='shadow_4',visibility='hidden',
                        datapath='gnr.explorers')
        tc = floating.tabContainer(margin='2px',selectedPage='^.selected_explorer')
        tc.dataController("SET .selected_explorer=show_explorer[0];",subscribe_show_explorer=True)
        for explorer in explorer_to_create:
            explorer_pars=None
            if ' AS ' in explorer:
                explorer,explorer_code = splitAndStrip(explorer,' AS ')
            elif ' as ' in explorer:
                explorer,explorer_code = splitAndStrip(explorer, ' as ')
            else:
                explorer_code = None
            if ':' in explorer:
                explorer,explorer_pars=explorer.split(':',1)
            if not explorer_code:
                explorer_code = explorer.replace('.','_').replace('@','_')
            handler= getattr(self,'explorer_'+explorer,None)
            pane=tc.contentPane(title=explorer,pageName=explorer_code,datapath='.%s' %explorer_code).contentPane(detachable=True)
            if handler:
                handler(pane,explorer_pars,explorer_code=explorer_code)
            else:
                if explorer_pars:
                    explorer_pars = fromJson(explorer_pars.replace("'",'"'))
                    kw = dict()
                    for k,v in explorer_pars.items():
                        kw[str(k)] = v
                else:
                    kw = dict()
                self.expmng_htableExplorer(pane,explorer_table=explorer,explorer_code=explorer_code,**kw)
        
    
    def expmng_htableExplorer(self,pane,explorer_table=None,explorer_code=None,**kwargs):
        tblobj = self.db.table(explorer_table)
        title=tblobj.name_long
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
                                    rootcaption=tblobj.name_plural,**kwargs)
        self.expmng_make_explorer(pane,data,explorer_code=explorer_code)        
                
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
                           
    def explorer_directory(self,pane,path=None,explorer_code=None):
        path = path or '/'
        pane.attributes['title'] = 'Directory:"%s"'%path
        self.expmng_make_explorer(pane,DirectoryResolver(path)(),explorer_code=explorer_code)
        
    def tableTreeResolver(self,table=None,where=None,group_by=None,**kwargs):
        tblobj = self.db.table(table)
        columns = [x for x in group_by if not callable(x)]    
        selection = tblobj.query(where=where,columns=','.join(columns),**kwargs).selection()
        explorer_id = self.getUuid()
        freeze_path = self.site.getStaticPath('page:explorers',explorer_id)
        totalizeBag = selection.totalize(group_by=group_by,collectIdx=False)
        return self.lazyBag(totalizeBag,name=explorer_id,location='page:explorer')
    
    def tableTreeExplorer(self,pane,table=None,where=None,group_by=None,explorer_code=None,**kwargs):
        data=self.tableTreeResolver(table=table,where=where,group_by=group_by,**kwargs)()
        explorer_code = explorer_code or table.replace('.','_')
        self.expmng_make_explorer(pane,data,explorer_code=explorer_code)
        