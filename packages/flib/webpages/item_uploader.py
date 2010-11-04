#!/usr/bin/env python
# encoding: utf-8
"""
Created by Softwell on 2009-02-23.
Copyright (c) 2009 Softwell. All rights reserved.
"""
from gnr.core.gnrbag import Bag


class GnrCustomWebPage(object):
    py_requires="""public:Public,public:IncludedView,gnrcomponents/htablehandler:HTablePicker,
                    gnrcomponents/drop_uploader,flib:FlibBase"""
    pageOptions={'enableZoom':False,'openMenu':False}
    
    def main(self, root, **kwargs):
        bc,top, bottom =self.pbl_rootBorderContainer(root,title='!!Upload file',datapath='uploader')
        left = bc.contentPane(region='left',width='150px',_class='pbl_roundedGroup',margin='2px',splitter=True)
        left.div('!!Categories',_class='pbl_roundedGroupLabel')
        self.htablePicker(left,nodeId='category_picker',
                            table='flib.category',datapath='category_picker',
                            output_pkeys='selected_categories',editMode='bc')
        left.dataController("FIRE reload_saved_files",_fired="^selected_categories")
        self.flibSavedFilesGrid(bc.contentPane(region='right',margin='2px',width='30%',_class='pbl_roundedGroup',splitter=True),
                                gridId='saved_files_grid',checked_categories='=selected_categories',reloader='^reload_saved_files')
        self.uploader_pane(bc.contentPane(region='center',margin='2px'))

    def uploader_pane(self,pane):
        def footer(footer,**kwargs):
            footer.button('Upload',action='PUBLISH flib_uploader_upload',float='right',
                            disabled='==!_selected_categories',
                            _selected_categories='^selected_categories')            
        self.dropFileGrid(pane,uploaderId='flib_uploader',datapath='.drop_filegrid',
                            label='!!Upload files',uploadPath='site:flib/items',
                            metacol_title=dict(name='!!Title',width='10em'),
                            metacol_description=dict(name='!!Descripton',width='15em'),
                            process_thumb32=True,
                            external_categories='=selected_categories',preview=True,
                            footer=footer,onResult='FIRE reload_saved_files;',
                            )
        pane.dataController("console.log('fatto');",subscribe_flib_uploader_done=True)
        
        
    def process_thumb32(self):
        return dict(fileaction='resize',height=32,filetype='png')
        
    def onUploading_flib_uploader(self,file_url=None,file_path=None,file_ext=None,categories=None,
                                description=None,title=None,action_results=None,**kwargs):
        item_table=self.db.table('flib.item')
        cat_table=self.db.table('flib.item_category')
        categories = categories.split(',')
        item_record=dict(path=file_path,url=file_url,description=description,title=title, 
                        username=self.user,ext=file_ext)
        metadata = Bag()
        if action_results['thumb32']:
            metadata['thumb32_url'] = action_results['thumb32']['file_url']
            metadata['thumb32_path'] = action_results['thumb32']['file_path']
        item_record['metadata'] = metadata

        existing_record = item_table.query(where='path=:p',p=file_path,for_update=True,addPkeyColumn=False).fetch()
        if existing_record:
            r = item_record
            item_record = dict(existing_record[0])
            item_record.update(r)
            item_table.update(item_record)
            cat_table.deleteSelection('item_id',item_record['id'])
        else:
            item_table.insert(item_record)
        for category_id in categories:
            if category_id:
                cat_table.insert(dict(category_id=category_id,item_id=item_record['id']))
        self.db.commit()
    
    def rpc_get_uploaded_files(self,selected_categories=None,current_range=None):
        tblobj = self.db.table('flib.item_category')
        categories = selected_categories.split(',')
        current_range = current_range or 20
        fetch = tblobj.query(columns='@item_id.ext AS ext,@item_id.url AS url, @item_id.title AS title, @item_id.description AS description,@item_id.metadata AS metadata',
                        where='$category_id IN :categories', 
                        categories=categories,limit=current_range,
                        order_by='$__ins_ts').fetch()
        result = Bag()
        if not fetch:
            return result
        for i,r in enumerate(fetch):
            info = dict()
            info['url'] = r['url']
            info['title'] = r['title']
            info['description'] = r['description']
            metadata = Bag(r['metadata'])
            ext_img = self.getResourceUri('filetype_icons/%s.png'%r['ext'][1:].lower()) or self.getResourceUri('filetype_icons/_blank.png')
            info['thumb'] = '<img border=0 height="32px" src="%s" />' %(metadata['thumb32_url'] or ext_img)
            result.setItem('r_%i' %i,None,_attributes=info) 
        return result
        
        
        