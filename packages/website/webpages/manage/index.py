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
    py_requires='public:Public,gnrcomponents/htablehandler:HTableHandler,gnrcomponents/selectionhandler,gnrcomponents/multiselect'
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
            parentBc = parentContainer.borderContainer(**kwargs)
            pane=parentBc.contentPane(region='top',**kwargs)
            editorPane=parentBc.contentPane(region='center',**kwargs)
            fb = pane.formbuilder(cols=2, border_spacing='4px', width="95%", fld_width="100%",dbtable=table)
            fb.field('title',validate_onAccept="""SET .permalink=toPermalink(value);""",width='50%')
            fb.field('permalink',lbl='!!Permalink',
                                                   validate_remote='permalink',
                                                   validate_id='=.id',
                                                   validate_parentCode='=.parent_code',
                                                   width='50%')
            fb.field('extended_title')
            fb.field('position')
            self.RichTextEditor(editorPane, value='^.content', height='70%',
                                toolbar=self.rte_toolbar_standard())
            
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