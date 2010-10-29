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
        left = bc.contentPane(region='left',width='150px',_class='pbl_roundedGroup',margin='2px',splitter=True)
        left.div('!!Categories',_class='pbl_roundedGroupLabel')
        self.htablePicker(left,nodeId='category_picker',
                            table='flib.category',datapath='category_picker',
                            output_pkeys='selected_categories',editMode='bc')
        left.dataController("FIRE reload_saved_files",_fired="^selected_categories")
        self.uploader_pane(bc.contentPane(region='center',margin='2px'))
       
        
       
    def saved_files_struct(self):
        struct = self.newGridStruct()
        r = struct.view().rows()
        r.cell("title",width='10em',title='!!Title')
        r.cell("description",width='15em',title='!!Description')
        r.cell("thumb",width='5em',title='!!Thumb')
        return struct
    
    def uploader_pane(self,pane):
        def footer(footer,**kwargs):
            footer.button('Upload',action='PUBLISH flib_uploader_upload',float='right')
        
        savedFilesGrid=dict(method='get_uploaded_files',
                                                selected_categories='=selected_categories',
                                                reloader='^reload_saved_files',
                                                current_range='=current_range')
        savedFilesGrid['struct'] = self.saved_files_struct()            
            
        self.dropFileGrid(pane,uploaderId='flib_uploader',datapath='.drop_filegrid',
                            label='!!Upload files',uploadPath='site:flib/items',
                            metacol_title=dict(name='!!Title',width='10em'),
                            metacol_description=dict(name='!!Descripton',width='15em'),
                            external_fileaction_resize48=dict(command='resize',dir='48x48',width=48),
                            external_fileaction_resize64=dict(command='resize',filetype='jpg'),
                            external_categories='=selected_categories',preview=True,
                            footer=footer,onResult='FIRE reload_saved_files;',
                            savedFilesGrid=savedFilesGrid)
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
    
    def rpc_get_uploaded_files(self,selected_categories=None,current_range=None):
        tblobj = self.db.table('flib.item_category')
        categories = selected_categories.split(',')
        current_range = current_range or 20
        data = tblobj.query(columns='@item_id.url AS url, @item_id.title AS title, @item_id.description AS description',
                        where='$category_id IN :categories', 
                        categories=categories,limit=current_range,
                        order_by='$__ins_ts').selection().output('grid')
        for n in data:
           n.attr['thumb']  = '<img border=0 width="40px" height="40px" src="%s" />' %n.attr['url']
           print n.attr
        return data
        
        
        