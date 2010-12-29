# -*- coding: UTF-8 -*-

# untitled.py
# Created by Francesco Porcari on 2010-11-13.
# Copyright (c) 2010 Softwell. All rights reserved.

from gnr.web.gnrbaseclasses import BaseComponent
from gnr.web.gnrwebstruct import struct_method
from gnr.core.gnrstring import splitAndStrip
from gnr.core.gnrbag import Bag,DirectoryResolver
from gnr.core.gnrdict import dictExtract
from gnr.core.gnrlang import debug_call
from time import time


class PaletteManager(BaseComponent):
    py_requires='foundation/macrowidgets:FilterBox,gnrcomponents/htablehandler:HTableHandlerBase,gnrcomponents/grid_configurator/grid_configurator:GridConfigurator'
    
    @struct_method
    def pm_paletteGroup(self,pane=None,groupCode=None,title=None,dockTo=None,**kwargs):
        floating = self._pm_floatingPalette(pane,nodeId='paletteGroup_%s_floating' %groupCode,
                                            title=title or '!!Palette %s' %groupCode,dockTo=dockTo,**kwargs)
        return floating.tabContainer(selectedPage='^gnr.palettes.?%s' %groupCode,groupCode=groupCode)
    
    def _pm_floating_kwargs(self,top=None,left=None,right=None,bottom=None,**kwargs):
        if (left is None) and (top is None) and (right is None) and (bottom is None):
            if not hasattr(self,'_last_floating'):
                self._last_floating = dict(top=0,right=0)
            self._last_floating['top']=self._last_floating['top']+10
            self._last_floating['right'] = self._last_floating['right'] +10
            top = '%ipx' %self._last_floating['top']
            right = '%ipx' %self._last_floating['right']
        palette_kwargs = dict(height='400px',width='300px',top=top,right=right,left=left,bottom=bottom,
                            visibility='hidden')
        palette_kwargs.update(kwargs)
        return palette_kwargs

    def _pm_floatingPalette(self,pane,nodeId=None,title=None,dockTo=None,**kwargs):
        dockTo = dockTo or 'default_dock'
        return pane.floatingPane(nodeId=nodeId,dockTo=dockTo,title=title,
                                    dockable=True,closable=False,resizable=True,
                                    **self._pm_floating_kwargs(**kwargs))
                                    
    @struct_method
    def pm_palettePane(self,pane,paletteCode=None,title=None,dockTo=None,**kwargs):
        groupCode = pane.parentNode.getInheritedAttributes().get('groupCode',None)
        if groupCode:
            pane = pane.contentPane(title=title,pageName=paletteCode) 
            pane.dataController("SET gnr.palettes?%s = paletteCode;" %groupCode,paletteCode=paletteCode, **{'subscribe_show_palette_%s' %paletteCode:True})
            return pane.contentPane(detachable=True,datapath='gnr.palettes.%s' %paletteCode,**kwargs)   
        else:
            parent = self._pm_floatingPalette(pane,'%s_floating' %paletteCode,title=title,dockTo=dockTo)
            return parent.contentPane(datapath='gnr.palettes.%s' %paletteCode,**kwargs)
            
    @struct_method
    def pm_paletteTree(self,pane,paletteCode=None,title=None,data=None,**kwargs):
        tree_kwargs = dict(labelAttribute='caption',_class='fieldsTree',hideValues=True,
                            margin='6px',font_size='.9em',draggable=True,
                            onDrag=""" if(treeItem.attr.child_count && treeItem.attr.child_count>0){
                                return false;
                            }
                            dragValues['text/plain']=treeItem.attr.caption;
                           dragValues['explorer_%s']=treeItem.attr;""" %paletteCode)
        tree_kwargs.update(dictExtract(kwargs,'tree_',pop=True))
        pane = pane.palettePane(paletteCode=paletteCode,title=title,**kwargs)
        if data is not None:
            pane.data('.store',data)
        pane.tree(storepath='.store',**tree_kwargs)
        return pane
        
    @struct_method
    def pm_paletteGrid(self,pane,paletteCode=None,title=None,data=None,struct=None,
                table=None,datamode=None,filterOn=None,configurable=None,**kwargs):
        grid_kwargs = dict(margin='6px',font_size='.9em',draggable_row=True,
                            onDrag="""dragValues['explorer_%s']=dragInfo.row;""" %paletteCode)
        grid_kwargs.update(dictExtract(kwargs,'grid_',pop=True))
        pane = pane.palettePane(paletteCode=paletteCode,title=title,**kwargs)
        gridId = 'palette_%s_grid' %paletteCode
        if filterOn:
            bc = pane.borderContainer()
            top = bc.contentPane(region='top').toolbar(height='20px')
            self.gridFilterBox(top.div(float='right'),gridId=gridId,filterOn=filterOn)
            pane = bc.contentPane(region='center')
        if data is not None:
            pane.data('.store',data)
        struct = struct or getattr(self,'palette_%s_struct' %paletteCode,None)
        pane.includedview(nodeId=gridId,storepath='.store',struct=struct,structpath='.grid.struct',
                          table=table,datamode=datamode,controllerPath='.grid',configurable=configurable,**grid_kwargs)
        return pane
        
    @struct_method
    def pm_directoryStore(self,pane,rootpath=None,storepath='.store',**kwargs):
        store = DirectoryResolver(rootpath or '/',**kwargs)()
        pane.data(storepath,store)
        
    @struct_method
    def pm_tableAnalyzeStore(self,pane,table=None,where=None,group_by=None,storepath='.store',**kwargs):
        t0 = time()
        tblobj = self.db.table(table)
        columns = [x for x in group_by if not callable(x)]    
        selection = tblobj.query(where=where,columns=','.join(columns),**kwargs).selection()
        explorer_id = self.getUuid()
        freeze_path = self.site.getStaticPath('page:explorers',explorer_id)
        t1 = time()
        totalizeBag = selection.totalize(group_by=group_by,collectIdx=False)
        t2 = time()
        store = self.lazyBag(totalizeBag,name=explorer_id,location='page:explorer')()
        t3 = time()
        pane.data(storepath,store,query_time=t1-t0,totalize_time=t2-t1,resolver_load_time=t3-t2)
        
    @struct_method
    def pm_htableStore(self,pane,table=None,related_table=None,relation_path=None,storepath='.store',**kwargs):
        if '@' in table:
            pkg,related_table,relation_path = table.split('.')
            related_table = '%s.%s' %(pkg,related_table)
            related_table_obj = self.db.table(related_table)
            table = related_table_obj.column(relation_path).parent.fullname
        tblobj = self.db.table(table)
        data = self.ht_treeDataStore(table=table,
                              related_table=related_table,
                              relation_path=relation_path,
                              rootcaption=tblobj.name_plural,**kwargs)
        pane.data(storepath,data)
        
    @struct_method
    def pm_selectionStore(self,pane,table=None,storepath='.store',nodeId=None,**kwargs):
        iv_node = pane.getNodeByAttr('tag', 'includedView')
        if iv_node:
            iv_attr = iv_node.attr
            table = table or iv_attr.get('table')
            if not nodeId:
                gridId = iv_attr.get('nodeId')
                if gridId:
                    nodeId = '%s_selection' %gridId
        pane.dataSelection(storepath,table,nodeId=nodeId,columns=kwargs.get('columns','=.grid.columns'),**kwargs)
        
    
