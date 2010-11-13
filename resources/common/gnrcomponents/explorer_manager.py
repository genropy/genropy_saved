# -*- coding: UTF-8 -*-

# untitled.py
# Created by Francesco Porcari on 2010-11-13.
# Copyright (c) 2010 Softwell. All rights reserved.

from gnr.web.gnrbaseclasses import BaseComponent

class ExplorerManager(BaseComponent):
    py_requires ='gnrcomponents/htablehandler:HTableHandlerBase'
    def onMain_explorer_manager(self):
        explorers = getattr(self,'explorers',None)
        if explorers:
            self.explorer_manager_main(explorers)
    
    def explorer_manager_draggable_types(self):
        return ','.join(['%s_item/json' %n.split('_',1)[1] for n in dir(self) if n.startswith('onDroppedItem_')])
       
    def explorer_manager_main(self,explorers):
        explorer_tables = explorers.split(',')
        pane = self.pageSource('pbl_bottomBarCenter').value
        pane.dock(id='explorer_dock',width='100px',background='none',border=0)
        floating = pane.floatingPane(title='!!Explorers',height='400px',width='300px',
                        top='100px',right='100px',closable=False,resizable=True,z_index=10000,persist=True,
                        dockable=True,dockTo='explorer_dock',_class='shadow_4',visibility='hidden',
                        datapath='gnr.explorers')
        tc = floating.tabContainer(margin='2px')
                        
        for explorer_table in explorer_tables:
            self.explorer_manager_create_explorer(tc,explorer_table)
        
    
    def explorer_manager_create_explorer(self,tc,explorer_table):
        rootpath = None
        if ':' in explorer_table:
            explorer_table,rootpath = explorer_table.split(':')
        
        tblobj = self.db.table(explorer_table)
        title=tblobj.name
        explorername = explorer_table.replace('.','_')
        epane = tc.contentPane(title=title,datapath='.%s' %explorername)
        related_field = None
        related_table = None
        if '@' in explorer_table:
            pkg,related_table,related_field = explorer_table.split('.')
            related_table = '%s.%s' %(pkg,related_table)
            related_table_obj = self.db.table(related_table)
            explorer_table = related_table_obj.column(related_field).parent.fullname
        epane.data('.data',self.ht_treeDataStore(table=explorer_table,
                                                related_table=related_table,
                                                relation_path=related_field,
                                                rootpath=rootpath,rootcaption=tblobj.name_plural))
        
        epane.tree(storepath='.data',
                labelAttribute='caption',
                 _class='fieldsTree',
                 hideValues=True,
                 margin='6px',
                 font_size='.9em',
                 node_draggable="""return item.attr.child_count==0 || !item.attr.child_count;""",                     
                 drag_mode='grid',              
                 drag_value_cb="""result = {'text/plain':item.attr.caption,
                                         '%s_item/json':item.attr}
                                  return result;""" %explorername,
                 drag_class='draggedItem')
            
