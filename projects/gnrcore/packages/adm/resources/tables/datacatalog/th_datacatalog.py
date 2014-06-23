#!/usr/bin/python
# -*- coding: UTF-8 -*-

from gnr.web.gnrbaseclasses import BaseComponent
from gnr.core.gnrdecorator import public_method

class View(BaseComponent):

    def th_struct(self,struct):
        r = struct.view().rows()
        r.fieldcell('code')
        r.fieldcell('description')
        r.fieldcell('rec_type')
        r.fieldcell('dtype')
        r.fieldcell('name_long')
        r.fieldcell('name_short')
        r.fieldcell('format')
        r.fieldcell('options')
        r.fieldcell('maxvalue')
        r.fieldcell('minvalue')
        r.fieldcell('dflt')
        r.fieldcell('tip')
        r.fieldcell('purpose')
        r.fieldcell('ext_ref')
        r.fieldcell('related_to')
        r.fieldcell('pkg')
        r.fieldcell('pkey_field')
        r.fieldcell('field_size')
        r.fieldcell('tbl')
        r.fieldcell('fld')
        r.fieldcell('comment')
        r.fieldcell('name_full')
        r.fieldcell('datacatalog_path')
        r.fieldcell('dbkey')

    def th_order(self):
        return 'code'

    def th_query(self):
        return dict(column='code', op='contains', val='')


class Form(BaseComponent):
    def th_form(self, form):
        tc = form.center.tabContainer()
        self.element_info(tc.borderContainer(title='Info',datapath='.record'))
        #self.element_permissions(tc.contentPane(title='Permissions'))

    def element_permissions(self,pane):
        th = pane.plainTableHandler(relation='@permissions',viewResource=':ViewFromCatalog')
        viewbar = th.view.top.bar
        viewbar.replaceSlots('#','#,picker')
        viewbar.picker.paletteTree('tag',tree_persist=True,
                                dockButton_iconClass='icnOpenPalette',
                                ).htableStore('adm.htag')        
        grid = th.view.grid
        grid.dragAndDrop(dropCodes='tag')
        
        grid.dataRpc("dummy",self.addPermission,data='^.dropped_tag', 
                     datacatalog_id='=#FORM.pkey')
        
    @public_method
    def addPermission(self,data=None,datacatalog_id=None):
        tag_id = data['pkey']
        tblpermission = self.db.table('adm.permission')
        if tblpermission.query(where='$tag_id=:t AND $datacatalog_id=:dc',dc=datacatalog_id,t=tag_id).count()==0:
            tblpermission.insert(dict(tag_id=tag_id,datacatalog_id=datacatalog_id))
            self.db.commit()
        
        
    def element_info(self,bc):
        top = bc.contentPane(region='top', _class='pbl_roundedGroup', margin='2px',height='50px')
        top.div().div(innerHTML='=="Base info:"+_rec_type', _rec_type='^.rec_type', _class='pbl_roundedGroupLabel')
        top.data('rec_type_fullmenu', self.db.table('adm.datacatalog').datacatalog_rec_types())
        fb = top.formbuilder(cols=2, border_spacing='4px', fld_width='15em', tdl_width='8em')
        fb.field('code')
        fb.field('description')
        center = bc.contentPane(region='center')
        center.remote(self.rec_type_main, rec_type='=.rec_type', _fired='^#FORM.controller.loaded')

    @public_method
    def rec_type_main(self, pane, rec_type=None,**kwargs):
        if not rec_type:
            return
        handler = getattr(self, 'remote_rec_type_%s' % rec_type, self.remote_rec_type_default)
        rec_type_dict = getattr(self.tblobj, 'rectype_%s' % rec_type)()
        handler(pane, rec_type_dict=rec_type_dict, **kwargs)

    def remote_rec_type_default(self, pane, rec_type_dict=None, **kwargs):
        bc = pane.borderContainer(height='100%')
        top = bc.contentPane(region='top')
        fb = top.formbuilder(cols=2, border_spacing='4px', fld_width='15em', tdl_width='8em')
        fields = rec_type_dict.get('fields')
        fields = fields.split(',') if fields else []
        for fld in fields:
            fb.field(fld)
        purpuse_width = '100%' if fields else '39em'
        fb.field('purpose', tag='simpleTextArea', height='6ex', colspan=2, width=purpuse_width,
                 lbl_vertical_align='top')
        center = bc.roundedGroupFrame(title='Comment',region='center', overflow='hidden')
        center.simpleTextArea(value='^.comment',editor=True)

    def remote_rec_type_group(self, pane, rec_type_dict=None,**kwargs):
        bc = pane.borderContainer(height='100%')
        top = bc.contentPane(region='top')
        fb = top.formbuilder(cols=2, border_spacing='4px', fld_widt='15em', tdl_width='8em')
        fb.field('name_short')
        fb.field('name_long')
        fb.field('purpose', tag='simpleTextArea', height='6ex', colspan=2, width='100%', lbl_vertical_align='top')
        center = bc.roundedGroupFrame(title='Comment',region='center', overflow='hidden')
        center.simpleTextArea(value='^.comment',editor=True)


    def remote_rec_type_db_field(self, pane, rec_type_dict=None, **kwargs):
        self.remote_rec_type_field(pane, rec_type_dict=rec_type_dict, **kwargs)

    def remote_rec_type_field(self, pane, rec_type_dict=None, **kwargs):
        bc = pane.borderContainer(height='100%')
        top = bc.contentPane(region='top')
        fb = top.formbuilder(cols=2, border_spacing='4px', fld_widt='15em', tdl_width='8em')
        fb.field('fld', tip='The name of the field')
        fb.field('dtype', tag='filteringSelect',
                 values='T:Text,L:Integer,N:Decimal,D:Date,H:Time,DH:Timestamp,B:Boolean')
        fb.field('name_short')
        fb.field('name_long')
        fb.field('field_size', tip='(eg: 2:5 means at least 2 chars, maximum 5 chars')
        fb.field('dflt', tip='Default value for the field')
        fb.field('minvalue', row_hidden='==_dtype?(_dtype!="L"&&_dtype!="N"):true', row__dtype='^.dtype')
        fb.field('maxvalue')
        fb.field('related_to', row_hidden='==_dtype?(_dtype=="D"||_dtype=="H"||_dtype=="DH"||_dtype=="B"):true',
                 row__dtype='^.dtype', tip='Drag from the explorer')
        fb.field('ext_ref')
        fb.field('options', colspan=2, width='100%', ghost='comma separated CODE:VALUE',
                 row_hidden='==_dtype?_dtype!="T":true', row__dtype='^.dtype')
        fb.field('purpose', tag='simpleTextArea', height='5ex', colspan=2, width='100%', lbl_vertical_align='top')
        center = bc.roundedGroupFrame(title='Comment',region='center', overflow='hidden')
        center.simpleTextArea(value='^.comment',editor=True)

    def th_options(self):
        return dict(hierarchical=True)
