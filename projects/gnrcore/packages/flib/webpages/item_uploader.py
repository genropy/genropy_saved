#!/usr/bin/env python
# encoding: utf-8
"""
Created by Softwell on 2009-02-23.
Copyright (c) 2009 Softwell. All rights reserved.
"""
from gnr.core.gnrbag import Bag


class GnrCustomWebPage(object):
    py_requires = """public:Public,gnrcomponents/htablehandler:HTablePicker,
                    gnrcomponents/drop_uploader,flib:FlibBase"""

    def main(self, root, **kwargs):
        frame = root.rootBorderContainer(title='!!Upload file', datapath='main')
        left = frame.contentPane(region='left', width='150px', _class='pbl_roundedGroup', margin='2px', splitter=True)
        left.div('!!Categories', _class='pbl_roundedGroupLabel')
        self.htablePicker(left, nodeId='category_picker',
                          table='flib.category', datapath='category_picker',
                          output_pkeys='selected_categories', editMode='bc')
        frame.contentPane(region='right', margin='2px',
                            splitter=True,width='300px').flibSavedFilesGrid(checked_categories='^selected_categories')
        self.uploader_pane(frame.contentPane(region='center', margin='2px'))

    def uploader_pane(self, pane):
        def footer(footer, **kwargs):
            footer.button('Upload', action='PUBLISH flib_uploader_upload', float='right',
                          disabled='==!_selected_categories',
                          _selected_categories='^selected_categories')

        pane.dropFileFrame(uploaderId='flib_uploader', datapath='.drop_filegrid',
                          label='!!Upload files', uploadPath='site:flib/items',
                          metacol_title=dict(name='!!Title', width='10em'),
                          metacol_description=dict(name='!!Descripton', width='15em'),
                          process_thumb32=True,
                          external_categories='=selected_categories', preview=True,
                          footer=footer,margin='2px',rounded=6,border='1px solid gray')


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

        
        