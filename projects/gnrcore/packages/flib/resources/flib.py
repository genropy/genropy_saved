# -*- coding: UTF-8 -*-

# item_uploader.py
# Created by Saverio Porcari on 2010-10-15.
# Copyright (c) 2010 __MyCompanyName__. All rights reserved.

from gnr.web.gnrwebpage import BaseComponent
from gnr.core.gnrbag import Bag
from gnr.web.gnrwebstruct import struct_method
class FlibBase(BaseComponent):
    py_requires = 'th/th:TableHandler'
    css_requires = 'public'
    
    @struct_method
    def flib_flibSavedFilesGrid(self, pane, checked_categories=None, reloader=None, label=None):
        storePars = dict(where="@categories.@category_id.code LIKE :cat_code || '%%'",
                             cat_code='^.#parent.tree.code',
                             applymethod='flibPickerThumb',
                             order_by='$title', _if='cat_code', _else='null')
        if checked_categories:
            storePars['where'] = '@categories.category_id IN :checked_categories'
            storePars['order_by'] = '$__ins_ts'
            storePars['limit'] = 100
            storePars['_if'] = None
            storePars['checked_categories'] = '^.checked_categories'
        th = pane.plainTableHandler(table='flib.item',viewResource=':LoadedFilesView')
        th.view.attributes.update(margin='2px',rounded=6,border='1px solid gray')
        if checked_categories:
            th.view.dataFormula('.checked_categories','checked_categories?checked_categories.split(","):[]',
                                checked_categories=checked_categories)
        storePars['startLocked'] = False
        th.view.store.attributes.update(storePars)
        th.view.grid.attributes.update(hiddencolumns='$__ins_ts,$thumb_url,$url,$ext,$metadata',
                             draggable_row=True,
                             onDrag="""
                                    var row = dragValues.gridrow.rowdata;
                                    dragValues['flib_element'] = row._pkey;                                
                             """)
        footer = th.view.bottom.slotBar('preview',closable='close',closable_tip='!!Preview',splitter=True)
        th.view.top.bar.replaceSlots('#','#,delrow')
        ppane = footer.preview.contentPane(height='200px',width='100%',_lazyBuild=True)
        sc = ppane.stackContainer(selectedPage='^.preview_type',margin='2px',)
        sc.dataController("""
                            var imageExt = ['.png','.jpg','.jpeg']
                            SET .preview_type = dojo.indexOf(imageExt,ext.toLowerCase())>=0?'image':'no_prev';
                            """, ext="^.grid.selectedId?ext")
        sc.contentPane(overflow='hidden', pageName='image',_class='pbl_roundedGroup').img(height='100%', src='^.grid.selectedId?url')
        sc.contentPane(pageName='no_prev',_class='pbl_roundedGroup').div(innerHTML='^.grid.selectedId?_thumb')


    def rpc_flibPickerThumb(self, selection):
        def apply_thumb(row):
            ext_img = self.getResourceUri('filetype_icons/%s.png' % row['ext'][1:].lower())\
            or self.getResourceUri('filetype_icons/_blank.png')
            return dict(_thumb='<img border=0 draggable="false" src="%s" />' % (row['thumb_url'] or ext_img))

        selection.apply(apply_thumb)


class FlibPicker(FlibBase):
    py_requires = """gnrcomponents/htablehandler:HTableHandlerBase"""

    def flibPicker(self, pane, pickerId=None, datapath=None, title=None, rootpath=None,
                   centerOn=None, limit_rec_type=None, dockTo=None, **kwargs):
        """"""
        dockTo = dockTo or 'default_dock'
        pane = pane.floatingPane(title=title or "!!File picker",
                                 height='400px', width='600px', nodeId=pickerId,
                                 top='100px', left='100px',
                                 dockTo=dockTo, visibility='hidden',
                                 dockable=True, closable=False, datapath=datapath,
                                 resizable=True, _class='shadow_4')
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

        bc.contentPane(region='center', margin='2px').flibSavedFilesGrid()
        
        
        