# -*- coding: UTF-8 -*-
#--------------------------------------------------------------------------
# Copyright (c) : 2004 - 2007 Softwell sas - Milano 
# Written by    : Giovanni Porcari, Michele Bertoldi
#                 Saverio Porcari, Francesco Porcari , Francesco Cavazzana
#--------------------------------------------------------------------------
#This library is free software; you can redistribute it and/or
#modify it under the terms of the GNU Lesser General Public
#License as published by the Free Software Foundation; either
#version 2.1 of the License, or (at your option) any later version.

#This library is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
#Lesser General Public License for more details.

#You should have received a copy of the GNU Lesser General Public
#License along with this library; if not, write to the Free Software
#Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA

class GnrCustomWebPage(object):
    maintable = 'adm.datacatalog'
    py_requires = """public:Public,gnrcomponents/htablehandler:HTableHandler,th/th:TableHandler,
                   gnrcomponents/batch_handler/batch_handler:TableScriptRunner,
                   gnrcomponents/batch_handler/batch_handler:BatchMonitor,
                """
    #explorers='adm.datacatalog'
    def windowTitle(self):
        return '!!Categories'

    def main(self, rootBC, **kwargs):
        bc, top, bottom = self.pbl_rootBorderContainer(rootBC, 'Categories')
        footer = bottom['left']
        footer.button('Import All',
                      action="PUBLISH table_script_run=params;",
                      params=dict(res_type='action', table=self.maintable, resource='import_datacatalog'))

        center = bc.borderContainer(region='center')
        self.htableHandler(center, table='adm.datacatalog', nodeId='datacatalog', rootpath=None,
                           datapath='datacatalog', editMode='bc', childTypes='rec_type_menu',
                           loadKwargs=dict(default_rec_type='=datacatalog.edit.childType'))

        top.dataController("""
                                var result = new gnr.GnrBag();
                                var rec_type_path = rec_type || 'main';
                                var children_rec_types = rec_type_fullmenu.getNode(rec_type_path).attr.children;
                                if (children_rec_types){
                                    children_rec_types= children_rec_types.split(',');
                                    dojo.forEach(children_rec_types,function(child_type){
                                        var caption=rec_type_fullmenu.getNode(child_type).attr.caption;
                                        result.setItem(child_type,null,{caption:caption});
                                    });
                                }
                                SET rec_type_menu = result;
                            """, rec_type_fullmenu="=rec_type_fullmenu",
                           rec_type='^.tree.rec_type',
                           _onStart=True,
                           datapath='datacatalog')

    def datacatalog_form(self, parentBC, table=None, disabled=None, **kwargs):
        tc = parentBC.tabContainer(**kwargs)
        self.element_info(tc.borderContainer(title='Info'),table=table,disabled=disabled)
        self.element_permissions(tc.contentPane(title='Permissions',datapath='#FORM'))

    def element_permissions(self,pane):
        th = pane.plainTableHandler(relation='@permissions',viewResource=':ViewFromCatalog')
        viewbar = th.view.top.bar
        viewbar.replaceSlots('#','#,picker')
        viewbar.picker.paletteTree('tag',tree_persist=True,
                                dockButton_iconClass='icnOpenPalette',
                                ).htableStore('adm.htag')        
        grid = th.view.grid
        grid.dragAndDrop(dropCodes='tag')
        
        grid.dataRpc("dummy","addPermission",data='^.dropped_tag', 
                     datacatalog_id='=#FORM.pkey')
        

    def rpc_updPermission(self,permission_id=None,fld=None,v=None):
        pass
    def rpc_addPermission(self,data=None,datacatalog_id=None):
        tag_id = data['pkey']
        tblpermission = self.db.table('adm.permission')
        if tblpermission.query(where='$tag_id=:t AND $datacatalog_id=:dc',dc=datacatalog_id,t=tag_id).count()==0:
            tblpermission.insert(dict(tag_id=tag_id,datacatalog_id=datacatalog_id))
            self.db.commit()
        
        
        
        
    def element_info(self,bc,table=None,disabled=None):
        top = bc.contentPane(region='top', _class='pbl_roundedGroup', margin='2px')
        top.data('#FORM.rec_type_fullmenu', self.db.table(table).datacatalog_rec_types())
        fb = top.formbuilder(cols=2, border_spacing='4px', fld_width='15em', tdl_width='8em', dbtable=table,
                             disabled=disabled)
        fb.field('child_code')
        fb.field('rec_type',storepath='#FORM.rec_type_fullmenu',tag='filteringSelect')
        fb.field('description')
        center = bc.contentPane(region='center')
        center.remote('rec_type_main', rec_type='^.rec_type')

    def remote_rec_type_main(self, pane, rec_type=None, disabled=None, **kwargs):
        if not rec_type:
            return
        handler = getattr(self, 'remote_rec_type_%s' % rec_type, self.remote_rec_type_default)
        rec_type_dict = getattr(self.tblobj, 'rectype_%s' % rec_type)()
        handler(pane, rec_type_dict=rec_type_dict, disabled=disabled, **kwargs)

    def remote_rec_type_default(self, pane, rec_type_dict=None, disabled=None, **kwargs):
        bc = pane.borderContainer(height='100%')
        top = bc.contentPane(region='top')
        fb = top.formbuilder(cols=2, border_spacing='4px', fld_width='15em', tdl_width='8em', disabled=disabled)
        fields = rec_type_dict.get('fields')
        fields = fields.split(',') if fields else []
        for fld in fields:
            fb.field(fld)
        purpuse_width = '100%' if fields else '39em'
        fb.field('purpose', tag='simpleTextArea', height='6ex', colspan=2, width=purpuse_width,
                 lbl_vertical_align='top')
        center = bc.contentPane(region='center', overflow='hidden')
        center.div('Comment', _class='pbl_roundedGroupLabel')
        self.RichTextEditor(center, value='^.comment', height='70%',
                            toolbar=self.rte_toolbar_standard())

    def remote_rec_type_group(self, pane, rec_type_dict=None, disabled=None, **kwargs):
        bc = pane.borderContainer(height='100%')
        top = bc.contentPane(region='top')
        fb = top.formbuilder(cols=2, border_spacing='4px', disabled=disabled, fld_widt='15em', tdl_width='8em')
        fb.field('name_short')
        fb.field('name_long')
        fb.field('purpose', tag='simpleTextArea', height='6ex', colspan=2, width='100%', lbl_vertical_align='top')
        center = bc.contentPane(region='center', overflow='hidden')
        center.div('Comment', _class='pbl_roundedGroupLabel')
        self.RichTextEditor(center, value='^.comment', height='70%',
                            toolbar=self.rte_toolbar_standard())

    def remote_rec_type_db_field(self, pane, rec_type_dict=None, disabled=None, **kwargs):
        self.remote_rec_type_field(pane, rec_type_dict=rec_type_dict, disabled=disabled, **kwargs)

    def remote_rec_type_field(self, pane, rec_type_dict=None, disabled=None, **kwargs):
        bc = pane.borderContainer(height='100%')
        top = bc.contentPane(region='top')
        fb = top.formbuilder(cols=2, border_spacing='4px', disabled=disabled, fld_widt='15em', tdl_width='8em')
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
        center = bc.contentPane(region='center', overflow='hidden')
        center.div('Comment', _class='pbl_roundedGroupLabel')
        self.RichTextEditor(center, value='^.comment', height='70%',
                            toolbar=self.rte_toolbar_standard())


        
        
    
