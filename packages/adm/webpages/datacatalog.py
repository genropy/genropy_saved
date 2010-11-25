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

from gnr.core.gnrdict import dictExtract

class GnrCustomWebPage(object):
    maintable='adm.datacatalog'
    py_requires="""public:Public,gnrcomponents/htablehandler:HTableHandler,
                   gnrcomponents/batch_handler/batch_handler:TableScriptRunner,
                   gnrcomponents/batch_handler/batch_handler:BatchMonitor
                """
    
    def windowTitle(self):
         return '!!Categories'
         
    def main(self, rootBC, **kwargs):
        bc,top,bottom = self.pbl_rootBorderContainer(rootBC,'Categories')
        footer = bc.contentPane(region='bottom')
        footer.button('Import All',
                    action="PUBLISH table_script_run=params;" ,
                    params=dict(res_type='action',table=self.maintable,resource='import_datacatalog'))
        
        
        center = bc.borderContainer(region='center')
        self.htableHandler(center,table='adm.datacatalog',nodeId='datacatalog',rootpath=None,
                            datapath='datacatalog',editMode='bc',childTypes='rec_type_menu',
                            loadKwargs=dict(default_rec_type='=datacatalog.edit.childType'))
                            
        top.dataController("""
                                var result = new gnr.GnrBag();
                                rec_type = rec_type || 'main';
                                var children_rec_types = rec_type_fullmenu.getNode(rec_type).attr.children;
                                if (children_rec_types){
                                    children_rec_types= children_rec_types.split(',');
                                    dojo.forEach(children_rec_types,function(child_type){
                                        var caption=rec_type_fullmenu.getNode(child_type).attr.caption;
                                        result.setItem(child_type,null,{caption:caption});
                                    });
                                }
                                SET rec_type_menu = result;
                            """,rec_type_fullmenu="=rec_type_fullmenu",
                                rec_type='^.edit.record.rec_type',_onStart=True,
                                datapath='datacatalog')
        
    def datacatalog_form(self,parentBC,table=None,disabled=None,**kwargs):
        bc = parentBC.borderContainer(**kwargs)
        top = bc.contentPane(region='top',_class='pbl_roundedGroup',margin='2px')
        top.div('Base Info',_class='pbl_roundedGroupLabel')
        top.data('rec_type_fullmenu',self.db.table(table).datacatalog_rec_types())        
        fb = top.div(margin='10px').formbuilder(cols=2, border_spacing='4px',width='100%',fld_width='100%',tdl_width='5em',dbtable=table,disabled=disabled)
        fb.field('child_code')
        fb.field('description')
        fb.div('^.rec_type',lbl='Rec type')
        center = bc.contentPane(region='center',_class='pbl_roundedGroup',margin='2px')
        center.div('Type info',_class='pbl_roundedGroupLabel')
        center.div().remote('rec_type_main',rec_type='=.rec_type',_fired='^.#parent.form.loaded',disabled_path=disabled)
        
    def remote_rec_type_main(self, pane,rec_type=None, disabled=None, **kwargs):
        if not rec_type:
            return
        handler = getattr(self,'remote_rec_type_%s' %rec_type,self.remote_rec_type_default)
        rec_type_dict = getattr(self.tblobj,'rectype_%s' %rec_type)()
        handler(pane,rec_type_dict=rec_type_dict, disabled=disabled, **kwargs) 
        
    def remote_rec_type_default(self,pane, rec_type_dict=None, disabled=None, **kwargs):  
        fb = pane.div(margin='10px').formbuilder(cols=2, border_spacing='4px',fld_width='100%',tdl_width='5em',disabled=disabled)
        
        fields = rec_type_dict.get('fields')
        fields = fields.split(',') if fields else []
        for fld in fields:
            fb.field(fld)
    
