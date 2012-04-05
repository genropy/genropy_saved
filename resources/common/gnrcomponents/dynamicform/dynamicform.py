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
                validate_regex_error='!!Invalid code: "." char is not allowed',validate_case='l',
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
        fb.field('source_checkboxtext',colspan=3,row_class='df_row field_checkboxtext',
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
        r.fieldcell('code', name='!!Code', width='5em')
        r.fieldcell('description', name='!!Description', width='15em')
        r.fieldcell('data_type', name='!!Type', width='10em')
        r.fieldcell('wdg_tag',name='!!Widget',width='10em')
        r.fieldcell('mandatory', name='!!Mandatory',width='7em') 
    
    def th_order(self):
        return '_row_count'

class DynamicForm(BaseComponent):
    py_requires='th/th:TableHandler,gnrcomponents/htablehandler:HTableHandlerBase'
    
    @struct_method
    def df_fieldsGrid(self,pane,title=None,searchOn=False,testForm=False,**kwargs):
        bc = pane.borderContainer()
        if testForm:
            mastertable = pane.getInheritedAttributes()['table']
            bc.contentPane(region='bottom',height='50%',splitter=True,margin_top='10px').dynamicFieldsPane(df_table=mastertable,df_pkey='=#FORM.pkey',
                                                    _fired='^#FORM.dynamicFormTester._refresh_fields',_mainrecordLoaded='^#FORM.controller.loaded',
                                                    datapath='#FORM.dynamicFormTester.data')
                
        
        th = bc.contentPane(region='center').paletteTableHandler(relation='@dynamicfields',formResource=':Form',viewResource=':View',
                                        grid_selfDragRows=True,configurable=False,default_data_type='T',
                                        grid_selfsubscribe_onExternalChanged='FIRE #FORM.dynamicFormTester._refresh_fields;',
                                        searchOn=searchOn,**kwargs)
        if title:
            th.view.data('.title',title)
        bar = th.view.top.bar.replaceSlots('*,delrow','fbfields,*,delrow')
        fb = bar.fbfields.formbuilder(cols=1, border_spacing='2px')
        fb.numberSpinner(value='^#FORM.record.df_fbcolumns',lbl='N. Col',width='3em',default_value=1)
        return th

    @struct_method
    def df_dynamicFieldsPane(self,pane,df_table=None,df_pkey=None,df_folders=None,**kwargs):
        pane.div().remote(self.df_remoteDynamicForm,df_table=df_table,df_pkey=df_pkey,
                    df_folders=df_folders,**kwargs)
                    


    
    @public_method
    def df_remoteDynamicForm(self,pane,df_table=None,df_pkey=None,df_folders=None,datapath=None,**kwargs):
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
        for r in fields:
            attr = dict(r)
            attr.pop('id')
            attr.pop('pkey')
            attr.pop('maintable_id')
            data_type = attr.pop('data_type','T')
            tag =  attr.pop('wdg_tag') or autowdg[data_type]
            if tag.endswith('_nopopup'):
                tag = tag.replace('_nopopup','')
                attr['popup'] = False
            attr['tag'] =tag

            #attr['colspan'] = col_max if data_type == 'TL' else 1
            
            attr['value']='^.%s' %attr.get('code')
            attr['lbl'] = '%s' %attr.pop('description','')
            attr['ghost'] = attr.pop('field_placeholder',None)
            attr['tip'] = attr.pop('field_tip',None)
            attr['style'] = attr.pop('field_style',None)
          #  attr['format'] = attr.pop('field_format',None)
            attr['colspan'] = attr.pop('wdg_colspan') or 1
            
            mask = attr.pop('field_mask',None)

            customizer = getattr(self,'df_%(tag)s' %attr,None)
            if customizer:
                customizer(attr,dbstore_kwargs=dbstore_kwargs)
            dictExtract(attr,'source_',pop=True)
            if tag == 'checkboxtext':
                attr.pop('tag')
                value = attr.pop('value')
                labels= attr.pop('labels')
                b = fb.div(lbl_vertical_align='top',width='100%',height='60px',lbl=attr.pop('lbl'),border='1px solid silver',rounded=4,**attr)
                subfb = b.tooltipPane().formbuilder(cols=1, border_spacing='2px')
                subfb.checkboxtext(labels=labels,value=value)
                b.div(value)
 
            else:
                self._df_handleFieldFormula(attr,fb=fb,fields=fields)
                self._df_handleFieldValidation(attr,fields=fields)
                attr.pop('code')
                fb.child(**attr)
            
           #self._df_handleFieldFormula(attr,fb=fb,fields=fields)
           #self._df_handleFieldValidation(attr,fb,fields=fields)

        
    def df_filteringselect(self,attr,**kwargs):
        attr['values'] = attr.get('source_filteringselect')
        
    def df_combobox(self,attr,**kwargs):
        attr['values'] = attr.get('source_combobox')
                    
    def df_dbselect(self,attr,dbstore_kwargs=None,**kwargs):
        tbl = attr.get('source_dbselect')
        attr['dbtable'] = tbl
        htbl = hasattr(self.db.table(tbl),'htableFields')
        pkg,tblname = tbl.split('.')
        attr['hasDownArrow'] =True
        if pkg in dbstore_kwargs:
            attr['_storename'] = '=%s' %dbstore_kwargs[pkg]

    def df_checkboxtext(self,attr,**kwargs):
        attr['labels'] = attr.get('source_checkboxtext')    
            
        
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
            
    