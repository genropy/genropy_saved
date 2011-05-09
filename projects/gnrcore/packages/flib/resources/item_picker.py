# -*- coding: UTF-8 -*-

# item_uploader.py
# Created by Saverio Porcari on 2010-10-15.
# Copyright (c) 2010 __MyCompanyName__. All rights reserved.

from gnr.web.gnrwebpage import BaseComponent
from gnr.core.gnrbag import Bag

class FlibPicker(BaseComponent):
    py_requires = """gnrcomponents/htablehandler:HTableHandlerBase,foundation/includedview:IncludedView"""
    css_requires = 'public'

    def flibPicker(self, pane, pickerId=None, datapath=None, title=None, rootpath=None,
                   centerOn=None, limit_rec_type=None, **kwargs):
        """"""
        pane = pane.floatingPane(title=title or "!!File picker",
                                 height='400px', width='600px', nodeId=pickerId, showOnStart=False,
                                 dockable=False, datapath=datapath, resizable=True, _class='shadow_4')
        pane.dataController("genro.wdgById(pickerId).show(); genro.dom.centerOn(pickerId,centerOn)",
                            centerOn=centerOn or "mainWindow",
                            pickerId=pickerId, **{'subscribe_%s_open' % pickerId: True})
        bc = pane.borderContainer()
        left = bc.contentPane(region='left', splitter=True, width='150px', _class='pbl_roundedGroup', margin='2px')
        left.data('.tree.store',
                  self.ht_treeDataStore(table='flib.category', rootpath=rootpath, rootcaption='!!Categories',
                                        rootcode='%'),
                  rootpath=rootpath)
        left.tree(storepath='.tree.store',
                  margin='10px', isTree=False, hideValues=True,
                  labelAttribute='caption',
                  selected_pkey='.tree.pkey', selectedPath='.tree.path',
                  selectedLabelClass='selectedTreeNode',
                  selected_code='.tree.code',
                  selected_caption='.tree.caption',
                  inspect='shift',
                  selected_child_count='.tree.child_count')

        center = bc.borderContainer(region='center', _class='pbl_roundedGroup', margin='2px')

        def saved_files_struct(struct):
            r = struct.view().rows()
            r.fieldcell("@item_id.title", width='10em', title='!!Title')
            r.fieldcell("@item_id.description", width='15em', title='!!Description')
            r.cell("_thumb", width='5em', title='!!Thumb', calculated=True)

        pickerGridId = '%s_grid' % pickerId

        self.includedViewBox(center.borderContainer(region='top', height='50%', splitter=True), label='!!Items',
                             datapath='.item_grid',
                             nodeId=pickerGridId, table='flib.item_category', autoWidth=True,
                             struct=saved_files_struct,
                             hiddencolumns='$item_id,@item_id.ext AS ext,@item_id.metadata AS meta,@item_id.url AS url',
                             reloader='^.#parent.tree.code',
                             onDrag='var dataNode = event.widget.dataNodeByIndex(event.rowIndex); return {flib_element:dataNode.attr.item_id};'
                             ,
                             filterOn='@item_id.title,@item_id.description',
                             selectionPars=dict(where="@category_id.code LIKE :cat_code || '%%'",
                                                cat_code='=.#parent.tree.code',
                                                applymethod='flibPickerThumb',
                                                order_by='@item_id.title'))

        sc = center.stackContainer(region='center', selectedPage='^.preview_type')
        sc.dataController("""
                            var imageExt = ['.png','.jpg','.jpeg']
                            SET .preview_type = dojo.indexOf(ext,imageExt)>=0?'image':'no_prev';
                            """, ext=".item_grid.selectedId?ext")
        sc.contentPane(overflow='hidden', pageName='image').img(height='100%', src='^.item_grid.selectedId?url')

        sc.contentPane(pageName='no_prev').div(innerHTML='^.item_grid.selectedId?_thumb')


    def rpc_flibPickerThumb(self, selection):
        def apply_thumb(row):
            ext_img = self.getResourceUri('filetype_icons/%s.png' % row['ext'][1:].lower())\
            or self.getResourceUri('filetype_icons/_blank.png')
            if row['meta']:
                metabag = Bag(row['meta'])
            return dict(_thumb='<img border=0 src="%s" height="32px" />' % (metabag['thumb32_url'] or ext_img))

        selection.apply(apply_thumb)
    
    
    
    

        
        