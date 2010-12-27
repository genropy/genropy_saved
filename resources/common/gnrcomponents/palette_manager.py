# -*- coding: UTF-8 -*-

# untitled.py
# Created by Francesco Porcari on 2010-11-13.
# Copyright (c) 2010 Softwell. All rights reserved.

from gnr.web.gnrbaseclasses import BaseComponent
from gnr.core.gnrstring import splitAndStrip
from gnr.core.gnrbag import DirectoryResolver
from gnr.core.gnrdict import dictExtract

class PaletteManager(BaseComponent):
    component_prefix='pm'
    def pm_paletteGroup(self,pane,groupCode=None,title=None,dockTo=None,**kwargs):
        floating = self._pm_floatingPalette(pane,nodeId='paletteGroup_%s_floating' %groupCode,
                                            title=title or '!!Palette %s' %groupCode,dockTo=dockTo,**kwargs)
        tcNodeId = 'paletteGroup_%s' %groupCode
        tc = floating.tabContainer(selectedPage='.selected',datapath='gnr.palettes.%s' %groupCode,
                                    nodeId=tcNodeId)
        tc.dataController("if(selected){SET .selected=page;}",
                           **{'subscribe_%s_select' %tcNodeId:True})
        return tc
    

    def _pm_floatingPalette(self,pane,nodeId=None,title=None,dockTo=None,**kwargs):
        palette_kwargs = dict(height='400px',width='300px',top='10px',right='10px',
                            visibility='hidden')
        palette_kwargs.update(kwargs)
        return pane.floatingPane(nodeId=nodeId,dockTo=dockTo,title=title,
                                    dockable=True,closable=False,**palette_kwargs)

    def pm_palettePane(self,pane,paletteCode=None,title=None,dockTo=None,**kwargs):
        if dockTo:
            parent = self._pm_floatingPalette(pane,'%s_floating' %paletteCode,title=title,dockTo=dockTo)
            return parent.contentPane(datapath='gnr.palettes.%s' %paletteCode,**kwargs)
        else:
            pane = pane.contentPane(title=title,pageName=paletteCode) 
            return pane.contentPane(detachable=True,datapath='gnr.palettes.%s' %paletteCode,**kwargs)
                
    def pm_paletteTree(self,paletteCode=None,paletteGroup=None,title=None,data=None,**kwargs):
        tree_kwargs = dict(labelAttribute='caption',_class='fieldsTree',hideValues=True,
                            margin='6px',font_size='.9em',draggable=True,
                            onDrag=""" if(treeItem.attr.child_count && treeItem.attr.child_count>0){
                                return false;
                            }
                            dragValues['text/plain']=treeItem.attr.caption;
                           dragValues['explorer_%s']=treeItem.attr;""" %paletteCode)
        tree_kwargs.update(dictExtract(kwargs,'tree_',pop=True))
        pane = self.palette(paletteGroup,pageName=paletteCode,title=title,**kwargs)
        pane.data('.data',data)
        pane.tree(storepath='.data',**tree_kwargs)