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

"""
Component for thermo:
"""
from gnr.web.gnrbaseclasses import BaseComponent
from gnr.core.gnrbag import Bag
from gnr.core.gnrdecorator import public_method
from gnr.core.gnrdict import dictExtract
from gnr.web.gnrwebstruct import struct_method
import re

class Form(BaseComponent):
    css_requires='gnrcomponents/dynamicform/dynamicform'
    js_requires='gnrcomponents/dynamicform/dynamicform'

    def th_form(self,form):
        bc = form.center.borderContainer(datapath='.record')
        bottom = bc.contentPane(region='bottom',border_top='1px solid silver')
        pane = bc.contentPane(region='center')
        box = pane.div(_class='^#FORM.boxClass',margin='5px',margin_top='10px',margin_right='15px')
        fb = box.formbuilder(cols=3, border_spacing='4px',tdl_width='5em',width='100%')
        tbl = pane.getInheritedAttributes()['table']
        fb.field('code',validate_notnull=True,validate_notnull_error='!!Required',width='8em', 
                validate_regex='!\.', 
                validate_regex_error='!!Invalid code: "." char is not allowed',#validate_case='l',
                validate_nodup=True,validate_nodup_error='!!Already existing code',
                validate_nodup_condition='$maintable_id=:fkey',validate_nodup_fkey='=#FORM.record.maintable_id',
                ghost='!!Field code')
        fb.field('description',validate_notnull=True,validate_notnull_error='!!Required',width='100%',colspan=2,
                    ghost='!!Field description')

        fb.field('data_type',values='!!T:Text,L:Integer,N:Decimal,D:Date,B:Boolean,H:Time,P:Image',width='8em',tag='FilteringSelect')
        fb.dataController("dynamicFormHandler.onDataTypeChange(this,data_type,_reason,this.form.isNewRecord());",data_type="^.data_type")

        fb.field('calculated',lbl='',label='!!Calculated')
        fb.dataController("dynamicFormHandler.onSetCalculated(this,calculated);",calculated="^.calculated")

        fb.br()
        
        fb.field('formula',colspan=3,width='100%',row_class='df_row field_calculated',lbl_vertical_align='top',height='60px',tag='simpleTextArea')
        
        fb.field('wdg_tag',values='^#FORM.allowedWidget',tag='filteringSelect',
                    row_class='df_row field_enterable')
        fb.dataController("dynamicFormHandler.onSetWdgTag(this,wdg_tag);",wdg_tag="^.wdg_tag")

        fb.field('wdg_colspan',width='4em')
        fb.br()
        
        fb.field('source_filteringselect',colspan=3,row_class='df_row field_filteringselect',
                tag='simpleTextArea',width='100%',lbl_vertical_align='top',height='60px',
                ghost='!!c1:description1\n c2:description2')
        fb.field('source_combobox',colspan=3,row_class='df_row field_combobox',
                tag='simpleTextArea',width='100%',lbl_vertical_align='top',height='60px',
                 ghost='!!description1\n description2')
        fb.field('source_checkboxtext',colspan=3,row_class='df_row field_checkboxtext field_checkboxtext_nopopup',
                tag='simpleTextArea',width='100%',lbl_vertical_align='top',height='60px',
                ghost='!!description1\n description2')
        fb.field('source_dbselect',colspan=3,row_class='df_row field_dbselect',width='100%',ghost='!!pkg.table')  
        
        
        fb.field('validate_case',width='8em',row_class='df_row field_textbox')
        fb.br()
        
        fb.field('validate_range',width='6em',row_class='df_row field_numbertextbox field_numberspinner field_currencytextbox')
        fb.br()
              
        
    
        
        footer = bottom.div(margin='5px',margin_right='15px').formbuilder(cols=2, border_spacing='4px',width='100%',fld_width='18em')
        
        footer.field('field_format',values='^#FORM.allowedFormat',tag='Combobox',lbl_width='4em')
        footer.field('field_placeholder',lbl_width='6em')
        footer.field('field_visible',lbl_vertical_align='top',height='60px',tag='simpleTextArea')
        footer.field('field_style',lbl_vertical_align='top',height='60px',tag='simpleTextArea')
        footer.field('field_tip',lbl_vertical_align='top',height='60px',tag='simpleTextArea')
        footer.field('field_mask',lbl_vertical_align='top',height='60px',tag='simpleTextArea')
    

    def th_options(self):
        return dict(palette_height='450px',palette_width='600px')


class View(BaseComponent):
    def th_struct(self,struct):
        r = struct.view().rows()
        r.fieldcell('_row_count',counter=True,hidden=True)
        r.fieldcell('code', name='!!Code', width='5em',draggable=True)
        r.fieldcell('description', name='!!Description', width='15em')
        r.fieldcell('data_type', name='!!Type', width='10em')
        r.fieldcell('wdg_tag',name='!!Widget',width='10em')
        r.fieldcell('mandatory', name='!!Mandatory',width='7em') 
    
    def th_order(self):
        return '_row_count'

class DynamicForm(BaseComponent):
    py_requires='th/th:TableHandler,gnrcomponents/htablehandler:HTableHandlerBase,foundation/macrowidgets:RichTextEditor'
    
    def __df_tpl_struct(self,struct):
        r = struct.view().rows()
        r.cell('tplname', name='Template', width='100%')
        
    def df_summaryTemplates(self,frame):
        bar = frame.top.slotToolbar('parentStackButtons,*,delgridrow,addrow_dlg')
        bc = frame.center.borderContainer(design='sidebar')
        fg = bc.frameGrid(region='left',margin='2px',storepath='#FORM.record.df_custom_templates',datamode='bag',
                            width='130px',struct=self.__df_tpl_struct,grid_selectedLabel='.selectedLabel',
                            grid_autoSelect=True)
        bar.addrow_dlg.slotButton('!!Add custom template',iconClass='iconbox add_row',
                                            action='genro.dlg.prompt(dlgtitle,{lbl:dlglbl,action:"FIRE #FORM.dynamicFormTester.newCustTpl=value;"},this);',
                                            dlgtitle='!!New template',dlglbl='!!Name')
        bar.delgridrow.slotButton('!!Delete selected template',iconClass='iconbox delete_row',
                                    action="""grid.publish("delrow");grid.widget.updateRowCount();
                                    """,grid=fg.grid)
        fg.dataController("""if(!currtemplates || currtemplates.len()==0){
            currtemplates = new gnr.GnrBag();
            currtemplates.setItem('base',new gnr.GnrBag({tpl:'',tplname:'base'}));
            SET #FORM.record.df_custom_templates = currtemplates;
        }else{
        console.log('fff',currtemplates);
        }
        """,currtemplates='=#FORM.record.df_custom_templates',_fired='^#FORM.controller.loaded')
        fg.dataController("""currtemplates.setItem(tplname,new gnr.GnrBag({tpl:'',tplname:tplname}));
                             setTimeout(function(){
                                grid.selection.select(grid.rowCount-1);
                             },1)
                                """,
                         tplname="^#FORM.dynamicFormTester.newCustTpl",
                          currtemplates='=#FORM.record.df_custom_templates',
                          grid=fg.grid.js_widget)
        fg.grid.dataFormula("#FORM.dynamicFormTester._editorDatapath", "'#FORM.record.df_custom_templates.'+selectedLabel;",
        selectedLabel="^.selectedLabel",_if='selectedLabel',_else='"#FORM.dynamicFormTester.dummypath"')
        center = bc.contentPane(region='center',datapath='^#FORM.dynamicFormTester._editorDatapath')
        self.RichTextEditor(center,value='^.tpl',toolbar='standard')
        
    @struct_method
    def df_fieldsGrid(self,pane,title=None,searchOn=False,**kwargs):
        bc = pane.borderContainer()
        mastertable = pane.getInheritedAttributes()['table']
        tc = bc.stackContainer(region='bottom',height='70%',splitter=True,hidden=True)
        self.df_previewForm(tc.framePane(title='!!Preview'),mastertable=mastertable)
        self.df_summaryTemplates(tc.framePane(title='!!Summary Templates'))        
        th = bc.contentPane(region='center').paletteTableHandler(relation='@dynamicfields',formResource=':Form',viewResource=':View',
                                        grid_selfDragRows=True,configurable=False,default_data_type='T',
                                        grid_onDrag="""
                                        if(dragInfo.dragmode=='cell' && dragInfo.colStruct.field=='code'){
                                            dragValues['text/plain'] = '$'+dragValues['text/plain'];
                                        }
                                        """,
                                        grid_selfsubscribe_onExternalChanged='FIRE #FORM.dynamicFormTester._refresh_fields = genro.getCounter();',
                                        searchOn=searchOn,**kwargs)
        if title:
            th.view.data('.title',title)
        bar = th.view.top.bar.replaceSlots('*,delrow','fbfields,showpreview,*,delrow')
        bar.showpreview.checkbox(value='^#FORM.dynamicFormTester.showpreview',label='Preview')
        bc.dataController("bc.setRegionVisible('bottom',prev)",bc=bc.js_widget,prev='^#FORM.dynamicFormTester.showpreview')
        fb = bar.fbfields.formbuilder(cols=1, border_spacing='2px')
        fb.numberSpinner(value='^#FORM.record.df_fbcolumns',lbl='N. Col',width='3em',default_value=1)
        return th

    def df_previewForm(self,frame,mastertable=None):
        bar = frame.top.slotToolbar('parentStackButtons,*,tplmenu,3')
        menuslot = bar.tplmenu.div()
        menuslot.div('^#FORM.dynamicFormTester.tplToShow',_class='floatingPopup',font_size='.9em',font_weight='bold',color='#555',cursor='pointer',padding='2px',rounded=4)
        menuslot.menu(_class='smallmenu',values='^#FORM.dynamicFormTester.menuvalues',modifiers='*',action='SET #FORM.dynamicFormTester.tplToShow = $1.label')
        menuslot.dataFormula("#FORM.dynamicFormTester.menuvalues", """currtemplates.keys().join(",");""",
                        currtemplates='^#FORM.dynamicFormTester.data._df_summaries',_if='currtemplates && currtemplates.len()',
                        _else='"auto"',_delay=1)
        menuslot.dataFormula("#FORM.dynamicFormTester.tplToShow","'auto'",_fired='^#FORM.record.loaded')
        
        bc = frame.center.borderContainer()
        bc.contentPane(region='right',width='40%',splitter=True,padding='10px').div(innerHTML='^#FORM.dynamicFormTester.tplRendered')
        bc.dataFormula("#FORM.dynamicFormTester.tplRendered", "summaries.getItem(tplToShow)",
                        summaries="^#FORM.dynamicFormTester.data._df_summaries",tplToShow='^#FORM.dynamicFormTester.tplToShow',
                        _delay=100,_if='summaries && summaries.len()>0')
        
        bc.contentPane(region='center',padding='10px').dynamicFieldsTestPane(df_table=mastertable,df_pkey='^#FORM.pkey',
                                                    _fired='^#FORM.dynamicFormTester._refresh_fields',
                                                    datapath='#FORM.dynamicFormTester.data',preview=True)

    @struct_method
    def df_dynamicFieldsPane_old(self,pane,df_table=None,df_pkey=None,**kwargs):
        pane.div().remote(self.df_remoteDynamicForm,df_table=df_table,df_pkey=df_pkey,**kwargs)
    
    
    @struct_method
    def df_dynamicFieldsTestPane(self,pane,df_table=None,df_pkey=None,**kwargs):
        pane.dataController("""if(_node.label!='_df_summaries'){
                                    dynamicFormHandler.onFieldsBagUpdated({templates:templates,data:data});
                                }""",
                        data="^#FORM.dynamicFormTester.data",
                        templates='^#FORM.record.df_custom_templates')
        pane.div().remote(self.df_remoteDynamicForm,df_table=df_table,df_pkey=df_pkey,cachedRemote=True,**kwargs)
        
    @struct_method
    def df_dynamicFieldsPane(self,pane,field=None,*kwargs):
        column = self.db.model.column(field) if '.' in field else self.db.table(pane.getInheritedAttributes()['table']).column(field)
        df_field = column.attributes['subfields']
        df_column = column.table(df_field)
        df_table = df_column.relatedTable()
        pane.div().remote(self.df_remoteDynamicForm,df_table=df_table.fullname,df_pkey='^#FORM.record.%s' %df_field,
                        **kwargs)
    
    @public_method
    def df_remoteDynamicForm(self,pane,df_table=None,df_pkey=None,datapath=None,**kwargs):
        if not df_pkey:
            pane.div()
            return
        dbstore_kwargs = dictExtract(kwargs,'dbstore_',pop=True)
        pane.attributes.update(kwargs)
        df_tblobj = self.db.table(df_table)
        fields = df_tblobj.df_getFieldsRows(pkey=df_pkey)
        ncol =df_tblobj.readColumns(columns='df_fbcolumns',pkey=df_pkey)
        autowdg = {'T':'TextBox','L':'NumberTextBox','D':'DateTextbox','R':'NumberTextBox','N':'NumberTextBox','H':'TimeTextBox','B':'CheckBox'};
        if not fields:
            return
        fb = pane.div(margin_right='10px').formbuilder(cols=ncol or 1,datapath=datapath)
        fieldsToDisplay = []
        
        for r in fields:
            attr = dict(r)
            attr.pop('id')
            attr.pop('pkey')
            attr.pop('maintable_id')
            data_type = attr.pop('data_type','T')
            tag =  attr.pop('wdg_tag') or autowdg[data_type]
            mask = attr.pop('field_mask',None)
            if tag.endswith('_nopopup'):
                tag = tag.replace('_nopopup','')
                attr['popup'] = False
            attr['tag'] =tag

            #attr['colspan'] = col_max if data_type == 'TL' else 1
            code = attr.get('code')
            description = attr.pop('description','')
            attr['value']='^.%s' %code
            fieldsToDisplay.append('%s:%s' %(description,code))
            attr['lbl'] = description
            attr['ghost'] = attr.pop('field_placeholder',None)
            attr['tip'] = attr.pop('field_tip',None)
            attr['style'] = attr.pop('field_style',None)
            
            attr['format'] = attr.pop('field_format',None)
            attr['dtype'] = data_type
            attr['mask'] = mask
            attr['colspan'] = attr.pop('wdg_colspan') or 1
            customizer = getattr(self,'df_%(tag)s' %attr,None)
            if customizer:
                customizer(attr,dbstore_kwargs=dbstore_kwargs)
            dictExtract(attr,'source_',pop=True)
            self._df_handleFieldFormula(attr,fb=fb,fields=fields)
            self._df_handleFieldValidation(attr,fields=fields)
            attr.pop('code')
            fb.child(**attr)
            
           #self._df_handleFieldFormula(attr,fb=fb,fields=fields)
           #self._df_handleFieldValidation(attr,fb,fields=fields)
        autoTemplate = ','.join(fieldsToDisplay)
        fb.data('._df_autotemplate',autoTemplate)


        
    def df_filteringselect(self,attr,**kwargs):
        attr['values'] = attr.get('source_filteringselect')
        
    def df_combobox(self,attr,**kwargs):
        attr['values'] = attr.get('source_combobox')
                

    def df_imguploader(self,attr,**kwargs):
        if not attr.get('style'):
            attr['height'] = '64px'
            attr['width'] = '64px'
        attr['placeholder'] = self.getResourceUri('images/imgplaceholder.png')
        attr['folder'] = "=='site:'+this.getInheritedAttributes()['table'].replace('.','/')+'%(code)s'" %attr
        attr['filename'] = '=#FORM.pkey'
        attr['dtype'] = 'T'
        attr['format'] = 'img'

    def df_dbselect(self,attr,dbstore_kwargs=None,**kwargs):
        tbl = attr.get('source_dbselect')
        attr['dbtable'] = tbl
        htbl = hasattr(self.db.table(tbl),'htableFields')
        pkg,tblname = tbl.split('.')
        attr['hasDownArrow'] =True
        if pkg in dbstore_kwargs:
            attr['_storename'] = '=%s' %dbstore_kwargs[pkg]

    def df_checkboxtext(self,attr,**kwargs):
        attr.setdefault('popup',True)
        attr['values'] = attr.get('source_checkboxtext')    
            
        
    def _df_handleFieldFormula(self,attr,fb,fields=None):
        formula = attr.pop('formula',None)
        if not formula:
            return
        formulaArgs = dict([(str(x['code']),'^.%s' %x['code']) for x in fields if x['code'] in formula])
        fb.dataFormula(".%s" %attr['code'], formula,**formulaArgs)
        attr['readOnly'] =True 
    
    def _df_handleFieldValidation(self,attr,fields):
        if attr.get('validate_range'):
            r = attr.pop('validate_range')
            min_v,max_v = r.split(':')
            if min_v or max_v:
                attr['validate_min'] = min_v or None
                attr['validate_max'] = max_v or None
                attr['validate_min_error'] = '!!Under min value %s' %min_v
                attr['validate_max_error'] = '!!Over max value %s' %max_v
        if attr.get('validate_case'):
            attr['validate_case'] = attr.pop('validate_case')
        if attr.get('field_visible'):
            condition = attr.pop('field_visible')
            attr['row_hidden'] = """==function(sourceNode){
                                        if(%s){
                                            return false;
                                        }else{
                                            sourceNode.setRelativeData('.%s',null);
                                            return true;
                                        }
                                    }(this);""" %(condition,attr['code'])
            conditionArgs = dict([('row_%s' %str(x['code']),'^.%s' %x['code']) for x in fields if x['code'] in condition])
            attr.update(conditionArgs)
            
    