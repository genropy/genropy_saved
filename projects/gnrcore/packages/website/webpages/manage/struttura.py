#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#
#  untitled
#
#  Created by Giovanni Porcari on 2007-03-24.
#  Copyright (c) 2007 Softwell. All rights reserved.
#

""" index.py """
# --------------------------- GnrWebPage subclass ---------------------------
from gnr.core.gnrbag import Bag

class GnrCustomWebPage(object):
    maintable='website.folder'
    py_requires="""public:Public,gnrcomponents/htablehandler:HTableHandler,
                   flib:FlibPicker, 
                   gnrcomponents/selectionhandler,gnrcomponents/multiselect"""
    js_requires='website'
    auto_polling=0
    pageOptions={'openMenu':False}

    
    def pageAuthTags(self, method=None, **kwargs):
        return 'user'
        
    def windowTitle(self):
         return '!!Struttura'
        
    def main(self, rootBC, **kwargs):
        bc,top,bottom = self.pbl_rootBorderContainer(rootBC,title='!!Structure')
        self.htableHandler(bc,table=self.maintable,nodeId='structureNode',rootpath=None,
                            datapath='structure',editMode='bc',plainView=False,
                            childsCodes=('.childs_ids','id')
                            )
    def structureNode_form(self,parentBC,table=None,disabled=None,**kwargs):
        bc = parentBC.borderContainer(**kwargs)
        top = bc.contentPane(region='top',_class='pbl_roundedGroup',margin='2px')
        top.div('!!Folder',_class='pbl_roundedGroupLabel')
        fb = top.formbuilder(cols=1, border_spacing='6px', fld_width='100%',width='100%',dbtable=table,disabled=disabled)
        fb.field('title',validate_onAccept="""SET .child_code=toPermalink(value)""")
        fb.field('extended_title')
        fb.field('child_code', lbl='!!Permalink',validate_remote='folderPermalink',
                                               validate_id='=.id',
                                               validate_parentCode='=.parent_code')
        fb.field('description',lbl='!!Description')
        fb.field('position')
        fb.dataController("""
                                if(!locked&&!id){
                                SET pages.can_add=false;
                                }
                            """,
                            locked='^pages.status.locked',
                            id="^structure.edit.record.id"
                            )
        
        def form(parentContainer,disabled,table,**kwargs):
            bc = parentContainer.borderContainer()
            formBc=bc.borderContainer(region='left',width='250px',**kwargs)
            editorPane=bc.contentPane(region='center',**kwargs)
            fb = formBc.contentPane(region='top',height='250px',_class='pbl_roundedGroup').formbuilder(cols=1, width="250px", fld_width="100%",dbtable=table)
            fb.field('title',validate_onAccept="""SET .permalink=toPermalink(value);""")
            fb.field('permalink',lbl='!!Permalink',
                                                   validate_remote='permalink',
                                                   validate_id='=.id',
                                                   validate_parentCode='=.parent_code')
            fb.field('extended_title',tag='textarea',height='100px')
            fb.field('position')
            fb.field('publish')
            fb.field('path',readOnly=True)
            self.RichTextEditor(editorPane, value='^.content', height='70%',
                                toolbar=self.rte_toolbar_standard(),config_resize_enabled='false')
            self.media(formBc.borderContainer(region='center',title='Media'))
            
        self.selectionHandler(bc.borderContainer(region='center',title=u'!!Pages'),
                    label=u'!!Pages',
                    parentId='^structure.tree.pkey',
                    table='website.page',
                    nodeId='pageGrid',
                    datapath='pages',
                    add_enable=True,
                    del_enable=True,
                    multiSelect=False,            
                    struct=self.db.table('website.page').folder_view,
                    reloader='^structure.childs_ids',
                    parentLock=disabled,
                    selectionPars=dict(where='$folder IN :child_folders',
                                       order_by='@folder.title,$position',
                                       child_folders='=structure.childs_ids',
                                       _if='child_folders',
                                       _else='null'),
                     dialogPars=dict(formCb=form,height='450px',width='800px',
                                       title='!!Page',
                                       default_folder='=structure.tree.pkey')
                                       )
    def media(self,bc):
        self.flibPicker(bc,pickerId='image_picker',datapath='media.picker',rootpath=None)
    
        def label(pane,disabled=None,**kwargs):
            pane.div(u'!!media',float='left')
            pane.button('!!Image picker',float='right',
                        action="""
                                var result = [];
                                selection.forEach(function(n){
                                    result.push(n.attr.flib_id);
                                });
                                result = result.join(',');   
                                SET media.curr_items = result;                 
                                PUBLISH image_picker_open;""",
                                selection='=media.selection')
            
        gridMedia = bc.borderContainer(region = 'top', height='250px')                     
        self.selectionHandler(gridMedia,label=label,
                    table='website.media',
                    nodeId='mediaGrid',
                    datapath='media',
                    multiSelect=False,            
                    struct=self.media_struct,
                    reloader='^pages.selectedId',
                    parentLock=False,
                    checkMainRecord=False,
                    selected_info_text='aux.currentMedia.text',
                    hiddencolumns='$info_text,$flib_id,@flib_id.ext AS ext',
                    dropTarget_grid='flib_element',
                    dropTarget=True,
                    dropTypes='flib_element',
                    onDrop_flib_element='FIRE .add_flib = data;',
                    selectionPars=dict(where='$page_id=:pageid',
                                       order_by='$title',
                                       pageid='=pages.selectedId',
                                       _if='pageid',
                                       applymethod='flibPickerThumbApply',
                                       _else='null'),
                    dialogPars=dict(height='400px',width='690px',
                                    title='!!Media',
                                    formCb=self.formMedia,
                                    default_page_id = '=pages.selectedId'))
        
        gridMedia.dataRpc('dummy','add_flib_item',item_id='^media.add_flib',pageid='=pages.selectedId',_onResult='FIRE media.reload;')
        
        previewAllegato = bc.contentPane(region='center').div(innerHTML="==dataTemplate(tpl,data)",
                    tpl="""<div>$text</div>
                           <img src=$url></img>""",
                           data='^aux.currentMedia')

    def media_struct(self,struct):
        r = struct.view().rows()
        r.cell('title', name='!!Title',width='10em')
        r.cell('@flib_id.url',name='!!File url',template='<a href="#">link</a>',width='5em')
        r.cell('_thumb',name='!!Thumb',width='5em',calculated=True)
        
    def formMedia(self, parentBC,disabled=False, **kwargs):
        bc = parentBC.borderContainer(**kwargs)
        #top = bc.contentPane(region='top',_class='pbl_roundedGroup')
        #center = bc.contentPane(region='center')
        #fb = top.formbuilder(dbtable='website.media', cols=2,width='100%',fld_width='100%',
        #                          border_spacing='5px',disabled=disabled)
        #fb.field('title', lbl='!!Title')

    def rpc_add_flib_item(self,item_id=None,pageid=None):
        tbl_media = self.db.table('website.media')
        flib_title = self.db.table('flib.item').readColumns(columns='$title',pkey=item_id)
        tbl_media.insert(dict(flib_id=item_id,page_id=pageid,title=flib_title))
        self.db.commit()

    def rpc_flibPickerThumbApply(self,selection):
        def apply_thumb(row):
            ext_img = self.getResourceUri('filetype_icons/%s.png'%row['ext'][1:].lower()) \
                      or self.getResourceUri('filetype_icons/_blank.png')
            return dict(_thumb= '<img border=0 src="%s" height="32px" />' %(row['_flib_id_url'] or ext_img))
        selection.apply(apply_thumb)
        
        
    def rpc_folderPermalink(self,value,**kwargs):
        result=self.db.table('website.folder').query(where='$child_code=:permalink',permalink=value).fetch()
        if not result:
            return True
        if not kwargs.get('id'):
            for r in result:
                if r['parent_code']==kwargs['parentCode']:
                    return  u'Invalid folder name, already exist at this position.'
        else:
            result=self.db.table('website.folder').query(where='$child_code=:permalink AND $parent_code=:pcode',
                                                                pcode=kwargs.get('parent_code',''),
                                                                permalink=value).fetch()                
            if result and result[0]['id']!=kwargs['id']:
                return u'Invalid folder name, already exist at this position.'
        return False
        
    def rpc_permalink(self,value,**kwargs):
        result=self.db.table('website.folder').query(where='$child_code=:permalink',permalink=value).fetch()
        if not result:
            return True
        if not kwargs.get('id'):
            for r in result:
                if r['parent_code']==kwargs['parentCode']:
                    return  u'Invalid folder name, already exist at this position.'
        else:
            result=self.db.table('website.folder').query(where='$child_code=:permalink AND $parent_code=:pcode',
                                                                pcode=kwargs.get('parent_code',''),
                                                                permalink=value).fetch()                
            if result and result[0]['id']!=kwargs['id']:
                return u'Invalid folder name, already exist at this position.'
        return False