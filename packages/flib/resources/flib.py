# -*- coding: UTF-8 -*-

# item_uploader.py
# Created by Saverio Porcari on 2010-10-15.
# Copyright (c) 2010 __MyCompanyName__. All rights reserved.

from gnr.web.gnrwebpage import BaseComponent
from gnr.core.gnrbag import Bag
class FlibBase(BaseComponent):
    py_requires='foundation/includedview:IncludedView'
    css_requires ='public'
    def flibSavedFilesGrid(self,pane,gridId,checked_categories=None,reloader=None,label=None):
        selectionPars=dict(where="@flib_item_category_item_id.@category_id.code LIKE :cat_code || '%%'",
                            cat_code='=.#parent.tree.code',
                            applymethod='flibPickerThumb',
                            order_by='$title',_if='cat_code',_else='null')
        if checked_categories:
            selectionPars['where'] = '@flib_item_category_item_id.category_id IN :checked_categories'
            selectionPars['checked_categories'] = '==_checked_categories?_checked_categories.split(","):[];'
            selectionPars['_if'] = '_checked_categories'
            selectionPars['_checked_categories'] = checked_categories
            selectionPars['order_by'] = '$__ins_ts'
            selectionPars['limit'] = 100
        
        bc = pane.borderContainer()
        
        def saved_files_struct(struct):
            r = struct.view().rows()
            r.fieldcell("title",width='10em',zoom=True)
            r.fieldcell("description",width='15em',zoom=True)
            r.cell("_thumb",width='5em',name='!!Thumb',calculated=True)
            
        self.includedViewBox(bc.borderContainer(region='top',height='50%',splitter=True),label=label or '!!Items',
                            datapath='.item_grid',
                             nodeId=gridId,table='flib.item',autoWidth=True,
                             struct=saved_files_struct,
                             hiddencolumns='$__ins_ts,$thumb_url,ext,metadata',
                             reloader=reloader,
                             drag_value_cb='var dataNode = event.widget.dataNodeByIndex(event.rowIndex); return {flib_element:dataNode.attr._pkey};',
                             filterOn='title,description',
                             selectionPars=selectionPars)
            
        sc = bc.stackContainer(region='center',selectedPage='^.preview_type')
        sc.dataController("""
                            var imageExt = ['.png','.jpg','.jpeg']
                            SET .preview_type = dojo.indexOf(ext,imageExt)>=0?'image':'no_prev';
                            """,ext=".item_grid.selectedId?ext")
        sc.contentPane(overflow='hidden',pageName='image').img(height='100%',src='^.item_grid.selectedId?url')
        sc.contentPane(pageName='no_prev').div(innerHTML='^.item_grid.selectedId?_thumb')

                                                
    def rpc_flibPickerThumb(self,selection):
        def apply_thumb(row):
            ext_img = self.getResourceUri('filetype_icons/%s.png'%row['ext'][1:].lower()) \
                      or self.getResourceUri('filetype_icons/_blank.png')
            return dict(_thumb= '<img border=0 src="%s" />' %(row['thumb_url'] or ext_img))
        selection.apply(apply_thumb)



class FlibPicker(FlibBase):
    py_requires="""gnrcomponents/htablehandler:HTableHandlerBase"""
    
    def flibPicker(self,pane,pickerId=None,datapath=None,title=None,rootpath=None,
                  centerOn=None,limit_rec_type=None,**kwargs):
        """"""
        pane = pane.floatingPane(title=title or "!!File picker",
                                height='400px',width='600px',nodeId=pickerId, showOnStart=False,
                                dockable=False,datapath=datapath,resizable=True,_class='shadow_4')
        pane.dataController("genro.wdgById(pickerId).show(); genro.dom.centerOn(pickerId,centerOn)",
                            centerOn=centerOn or "mainWindow",
                            pickerId=pickerId,**{'subscribe_%s_open'%pickerId:True})
        bc = pane.borderContainer()
        left = bc.contentPane(region='left',splitter=True,width='150px',_class='pbl_roundedGroup',margin='2px')             
        left.data('.tree.store',self.ht_treeDataStore(table='flib.category',rootpath=rootpath,rootcaption='!!Categories',rootcode='%'),
                    rootpath=rootpath)
        left.tree(storepath ='.tree.store',
                    margin='10px',isTree =False,hideValues=True,
                    labelAttribute ='caption',
                    selected_pkey='.tree.pkey',selectedPath='.tree.path',  
                    selectedLabelClass='selectedTreeNode',
                    selected_code='.tree.code',
                    selected_caption='.tree.caption',
                    inspect='shift',
                    selected_child_count='.tree.child_count')
                    
            
        self.flibSavedFilesGrid(bc.contentPane(region='center',margin='2px'),reloader='^.#parent.tree.code',
                                gridId='%s_grid' %pickerId)
        
        
        