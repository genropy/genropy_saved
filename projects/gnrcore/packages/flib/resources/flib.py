# -*- coding: UTF-8 -*-

# item_uploader.py
# Created by Saverio Porcari on 2010-10-15.
# Copyright (c) 2010 __MyCompanyName__. All rights reserved.

from gnr.web.gnrwebpage import BaseComponent
from gnr.core.gnrbag import Bag
from gnr.web.gnrwebstruct import struct_method
from gnr.core.gnrdecorator import extract_kwargs
class FlibBase(BaseComponent):
    py_requires = 'th/th:TableHandler'
    css_requires = 'public'
    
    @struct_method
    def flib_flibSavedFilesGrid(self, pane, checked_categories=None, reloader=None, label=None,
                                viewResource=None,preview=None,configurable=False):
        viewResource = viewResource or ':LoadedFilesView'
        th = pane.inlineTableHandler(table='flib.item',configurable=configurable,pbl_classes=True,
                        viewResource=viewResource,nodeId='flib_item_%s' %id(pane),margin='2px',autoSave=True,
                        addrow=False,delrow=True)
        if checked_categories:
            storePars = {}
            storePars['where'] = '@categories.category_id IN :checked_categories'
            storePars['order_by'] = '$__ins_ts'
            storePars['limit'] = 1000
            storePars['checked_categories'] = '^.checked_categories'
            th.view.dataFormula('.checked_categories','checked_categories?checked_categories.split(","):[]',
                                checked_categories=checked_categories)
            storePars['startLocked'] = False
            th.view.store.attributes.update(storePars)
        th.view.grid.attributes.update(hiddencolumns='$__ins_ts,$thumb_url,$url,$ext,$metadata')
        if preview:
            footer = th.view.bottom.slotBar('preview',closable='close',closable_tip='!!Preview',splitter=True)
            ppane = footer.preview.contentPane(height='200px',width='100%',_lazyBuild=True)
            sc = ppane.stackContainer(selectedPage='^.preview_type',margin='2px',)
            sc.dataController("""
                                var imageExt = ['.png','.jpg','.jpeg']
                                SET .preview_type = dojo.indexOf(imageExt,ext.toLowerCase())>=0?'image':'no_prev';
                                """, ext="^.grid.selectedId?ext")
            sc.contentPane(overflow='hidden', pageName='image',_class='pbl_roundedGroup').img(height='100%', src='^.grid.selectedId?url')
            sc.contentPane(pageName='no_prev',_class='pbl_roundedGroup').div(innerHTML='^.grid.selectedId?_thumb')
        return th
    
    



class FlibPicker(FlibBase):
    def flibPicker(self, pane, pickerId=None, datapath=None, title=None, rootpath=None,
                   centerOn=None, limit_rec_type=None, dockTo=None, **kwargs):
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
        left.hTableTree(storepath='.tree.store',table='flib.category',
                  margin='10px', isTree=False, hideValues=True,
                  labelAttribute='caption',
                  selected_pkey='.tree.pkey', selectedPath='.tree.path',
                  selectedLabelClass='selectedTreeNode',
                  selected_hierarchical_pkey='.tree.hierarchical_pkey',
                  selected_caption='.tree.caption',
                  inspect='shift',
                  selected_child_count='.tree.child_count')
        bc.contentPane(region='center', margin='2px').flibSavedFilesGrid()
        
    @struct_method
    def flib_flibPicker(self, pane, paletteCode=None, title=None, rootpath=None,
                   limit_rec_type=None, viewResource=None,**kwargs):
        pane = pane.palettePane(paletteCode or 'flibPicker',
                                title=title or "!!File picker",
                                height='400px', width='600px',**kwargs)
        
        pane.flibPickerPane(limit_rec_type=limit_rec_type,rootpath=rootpath,
                            gridpane_region='center', gridpane_margin='2px',
                            treepane_region='left',treepane_margin='2px',treepane_splitter=True,
                            treepane__class='pbl_roundedGroup',treepane_width='150px',viewResource=viewResource)
    
    @extract_kwargs(treepane=True,gridpane=True)
    @struct_method
    def flib_flibPickerPane(self,pane,rootpath=None,limit_rec_type=None,preview=True,viewResource=None,treepane_kwargs=None,gridpane_kwargs=None):
        bc = pane.borderContainer()
        left = bc.contentPane(**treepane_kwargs)
        pickerTreeId = 'flibPickerTree_%s' %id(left)
        left.div(position='absolute',top='1px',left='1px',bottom='1px',right='1px',overflow='auto').hTableTree(storepath='.tree.store',
                  nodeId=pickerTreeId,table='flib.category',
                  margin='10px', isTree=False, hideValues=True,
                  labelAttribute='caption',
                  selected_pkey='.tree.pkey', selectedPath='.tree.path',
                  selectedLabelClass='selectedTreeNode',
                  selected_hierarchical_pkey='.tree.hierarchical_pkey',
                  selected_caption='.tree.caption',
                  inspect='shift',
                  selected_child_count='.tree.child_count')
        th = bc.contentPane(**gridpane_kwargs).flibSavedFilesGrid(viewResource=viewResource,preview=preview)
        th.view.store.attributes.update(dict(where="@categories.@category_id.hierarchical_pkey LIKE :cat_hierarchical_pkey || '/%%'",
                             cat_hierarchical_pkey='^#%s.tree.hierarchical_pkey' %pickerTreeId,
                             order_by='$title', _if='cat_hierarchical_pkey', _else='null'))
        return bc
        
class FlibUploaderMain(BaseComponent):
    py_requires = """public:Public,gnrcomponents/drop_uploader,flib:FlibBase"""

    def main(self, root, **kwargs):
        frame = root.rootBorderContainer(title='!!Upload file', datapath='main')
        left = frame.contentPane(region='left', width='150px', overflow='auto',
                                _class='pbl_roundedGroup',
                                 margin='2px', splitter=True)
        left.div('!!Categories', _class='pbl_roundedGroupLabel')  
        left.hTableTree(storepath='.tree.store',table='flib.category',
                  margin='10px', isTree=False, hideValues=True,
                  labelAttribute='caption',nodeId='category_picker',
                  selected_pkey='.tree.pkey', selectedPath='.tree.path',
                  selectedLabelClass='selectedTreeNode',
                  selected_hierarchical_pkey='.tree.hierarchical_pkey',
                  selected_caption='.tree.caption',
                  inspect='shift',resolved=True,
                  checked_pkey='selected_categories',
                  selected_child_count='.tree.child_count')
        frame.contentPane(region='right', margin='2px',
                            splitter=True,width='300px').flibSavedFilesGrid(checked_categories='^selected_categories')
        self.uploader_pane(frame.contentPane(region='center', margin='2px'))

    def uploader_pane(self, pane):
        def footer(footer, **kwargs):
            footer.button('Upload', action='PUBLISH flib_uploader_upload', float='right',
                          disabled='==!_selected_categories',
                          _selected_categories='^selected_categories')

        pane.dropFileFrame(uploaderId='flib_uploader', datapath='.drop_filegrid',
                          label='!!Upload files', uploader_path=self.db.table('flib.item').getUploadPath(),
                          metacol_title=dict(name='!!Title', width='10em'),
                          metacol_description=dict(name='!!Descripton', width='15em'),
                          process_thumb32=True,
                          external_categories='=selected_categories', preview=True,
                          footer=footer,margin='2px',pbl_classes=True)


    def process_thumb32(self):
        return dict(fileaction='resize', height=32, filetype='png')

    def onUploading_flib_uploader(self, file_url=None, file_path=None, file_ext=None, categories=None,
                                  description=None, title=None, action_results=None, **kwargs):
        item_table = self.db.table('flib.item')
        cat_table = self.db.table('flib.item_category')
        categories = categories.split(',')
        item_record = dict(path=file_path, url=file_url, description=description, title=title,
                           username=self.user, ext=file_ext)
        versions = Bag()
        if action_results['thumb32']:
            thumb_url = action_results['thumb32']['file_url']
            thumb_path = action_results['thumb32']['file_path']
            item_record['thumb_url'] = thumb_url
            item_record['thumb_path'] = thumb_path
            versions['thumb32_url'] = thumb_url
            versions['thumb32_path'] = thumb_path
        item_record['versions'] = versions
        existing_record = item_table.query(where='path=:p', p=file_path, for_update=True, addPkeyColumn=False).fetch()
        if existing_record:
            r = item_record
            item_record = dict(existing_record[0])
            item_record.update(r)
            item_table.update(item_record)
            cat_table.deleteSelection('item_id', item_record['id'])
        else:
            item_table.insert(item_record)
        for category_id in categories:
            if category_id:
                cat_table.insert(dict(category_id=category_id, item_id=item_record['id']))
        self.db.commit()
        
        