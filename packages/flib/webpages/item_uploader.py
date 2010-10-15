#!/usr/bin/env python
# encoding: utf-8
"""
Created by Softwell on 2009-02-23.
Copyright (c) 2009 Softwell. All rights reserved.
"""

class GnrCustomWebPage(object):
    py_requires="""public:Public,public:IncludedView,gnrcomponents/htablehandler:HTablePicker,gnrcomponents/drop_uploader"""
    pageOptions={'enableZoom':False,'openMenu':False}
    
    def main(self, root, **kwargs):
        bc,top, bottom =self.pbl_rootBorderContainer(root,title='!!Upload file',datapath='uploader')
        self.htablePicker(bc.contentPane(region='left',width='150px'),nodeId='category_picker',
                            table='flib.category',
                            output_pkeys='selected_categories',editMode='bc')

        self.uploader_pane(bc.contentPane(region='center'))
       
    def uploader_pane(self,pane):
        def footer(footer,**kwargs):
            footer.button('Upload',action='PUBLISH flib_uploader_upload',float='right')
                                
        self.dropFileGrid(pane,uploaderId='flib_uploader',datapath='.drop_filegrid',
                            label='!!Uploaded files',uploadPath='site:flib/items',
                            metacol_title=dict(name='!!Title',width='10em'),
                            metacol_description=dict(name='!!Descripton',width='15em'),
                            external_categories='=selected_categories',preview=True,
                            footer=footer)
        pane.dataController("console.log('fatto');",subscribe_flib_uploader_done=True)
        
    def onUploading_flib_uploader(self,file_url=None,file_path=None,categories=None,
                                description=None,title=None,**kwargs):
        item_table=self.db.table('flib.item')
        cat_table=self.db.table('flib.item_category')
        categories = categories.split(',')
        item_record=dict(path=file_path,url=file_url,description=description,title=title, username=self.user)
        f = item_table.query(where='path=:p',p=file_path,for_update=True,addPkeyColumn=False).fetch()
        if f:
            r = item_record
            item_record = dict(f[0])
            item_record.update(r)
            item_table.update(item_record)
            cat_table.deleteSelection('item_id',item_record['id'])
        else:
            item_table.insert(item_record)
        for category_id in categories:
            cat_table.insert(dict(category_id=category_id,item_id=item_record['id']))
        self.db.commit()
