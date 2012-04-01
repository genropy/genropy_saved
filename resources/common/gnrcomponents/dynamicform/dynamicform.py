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
        
        fb.field('code',validate_notnull=True,validate_notnull_error='!!Required',width='8em', 
                validate_regex='!\.', 
                validate_regex_error='!!Invalid code: "." char is not allowed',validate_case='l')
        fb.field('description',validate_notnull=True,validate_notnull_error='!!Required',width='100%',colspan=2)

        fb.field('data_type',values='!!T:Text,L:Integer,N:Decimal,D:Date,B:Boolean,H:Time,P:Image',width='8em',tag='FilteringSelect')
        fb.field('calculated',lbl='',label='!!Calculated')
        fb.br()
        
        fb.field('formula',colspan=3,width='100%',row_class='df_row field_calculated',lbl_vertical_align='top',height='60px',tag='simpleTextArea')
        
        fb.field('wdg_tag',values='^#FORM.allowedWidget',tag='filteringSelect',row_class='df_row field_enterable')
        fb.dataController("dynamicFormHandler.onSetWdgTag(this,wdg_tag);",wdg_tag="^.wdg_tag")
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
        
        
        #fb.field('caps')
              
        fb.dataController("dynamicFormHandler.onSetCalculated(this,calculated);",calculated="^.calculated")
        
        fb.dataController("dynamicFormHandler.onDataTypeChange(this,data_type);",data_type="^.data_type")
        
        
        
        footer = bottom.div(margin='5px',margin_right='15px').formbuilder(cols=2, border_spacing='4px',lbl_width='4em',width='100%',fld_width='18em')
        
        footer.field('field_format',values='^#FORM.allowedFormat',tag='Combobox')
        footer.br()
        footer.field('field_visible',lbl_vertical_align='top',height='60px',tag='simpleTextArea')
        footer.field('field_style',lbl_vertical_align='top',height='60px',tag='simpleTextArea')
        footer.field('field_tip',lbl_vertical_align='top',height='60px',tag='simpleTextArea')
        footer.field('field_mask',lbl_vertical_align='top',height='60px',tag='simpleTextArea')

        
    def xxx(self,fb):
        
       #fb.field('field_type',values='!!T:Text,TL:Long Text,DB:Db link,L:Integer,N:Decimal,D:Date,B:Boolean,H:Time,F:Formula',
       #         validate_notnull=True,validate_notnull_error='!!Required',width='8em',tag='filteringSelect')
                 
        fb.dataController("""SET #FORM.boxClass = data_type? 'dffb_'+data_type:'';""",
                        box=box,data_type='^.data_type')
        
        fb.field('description',validate_notnull=True,validate_notnull_error='!!Required',width='100%',colspan=2)

        fb.field('source_values',colspan=2,row_class='df_row T_R',
                tag='simpleTextArea',width='100%',lbl_vertical_align='top',height='60px')
                
        fb.field('caps',row_class='df_row T_R',row_hidden='^.source_values',colspan=2,width='100%')
        
        fb.field('source_multivalues',row_class='df_row TL_R',
                colspan=2,tag='simpleTextArea',width='100%',lbl_vertical_align='top',height='60px',
                lbl='Multiple values',
                ghost="""!!A string separated by comma set of words. For every words there will be created a single checkbox""")
                
        fb.field('field_style',colspan=2,width='100%',lbl_vertical_align='top',height='60px',tag='simpleTextArea',
                row_class='df_row TL_R')
                
        fb.field('source_table',colspan=2,width='100%',row_class='df_row DB_R')
        
        fb.field('range',ghost='min:max',row_class='df_row N_R L_R',width='8em')
        fb.field('standard_range',ghost='min:max',width='8em')
        
        fb.field('formula',colspan=2,width='100%',row_class='df_row F_R')
        
        fb.field('condition',width='100%',colspan=2,lbl_vertical_align='top',height='60px',tag='simpleTextArea')
        fb.field('mandatory',lbl='',label='!!Mandatory')

    
    def th_options(self):
        return dict(dialog_height='450px',dialog_width='600px')


class View(BaseComponent):
    def th_struct(self,struct):
        r = struct.view().rows()
        r.fieldcell('_row_count',counter=True)
        r.fieldcell('code', name='!!Code', width='5em')
        r.fieldcell('description', name='!!Description', width='15em')
        r.fieldcell('data_type', name='!!Type', width='10em')
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
            bc.contentPane(region='bottom',height='50%',splitter=True,margin_top='10px').dynamicFieldsPane(df_table=mastertable,df_pkey='^#FORM.pkey',
                                                    _fired='^#FORM.dynamicFormTester._refresh_fields',
                                                    datapath='#FORM.dynamicFormTester.data')
        
        th = bc.contentPane(region='center').paletteTableHandler(relation='@dynamicfields',formResource=':Form',viewResource=':View',
                                        grid_selfDragRows=True,configurable=False,default_data_type='T',
                                        grid_selfsubscribe_onExternalChanged='FIRE #FORM.dynamicFormTester._refresh_fields;',
                                        searchOn=searchOn,**kwargs)
        if title:
            th.view.data('.title',title)

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
        if not fields:
            return
        fb = pane.div(margin_right='10px').formbuilder(cols=1,datapath=datapath)
        for r in fields:
            attr = dict(r)
            attr.pop('id')
            attr.pop('pkey')
            attr.pop('maintable_id')
            data_type = attr.pop('data_type','T')
            tag =  attr.pop('wdg_tag','textbox')
            attr['tag'] =tag
            if tag.endswith('_nopopup'):
                tag = tag.replace('_nopopup','')
                attr['_popup'] = False
            #attr['colspan'] = col_max if data_type == 'TL' else 1
            
            attr['value']='^.%s' %attr.pop('code')
            attr['lbl'] = '%s' %attr.pop('description',''),
            customizer = getattr(self,'df_%(tag)s' %attr,None)
            if customizer:
                customizer(attr,dbstore_kwargs=dbstore_kwargs)
            dictExtract(attr,'source_',pop=True)
            if tag == 'checkboxtext':
                attr.pop('tag')
                fb.checkboxtext(**attr)
            else:
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
        formulaArgs = dict([(str(x),'^.%s' %x) for x in fields.digest('#a.code') if x in formula])
        fb.dataFormula(".%s" %attr['code'], formula,**formulaArgs)
        attr['readOnly'] =True 
    
    def _df_handleFieldValidation(self,attr,fb,fields):
        if attr.get('range'):
            r = attr.pop('range')
            min_v,max_v = r.split(':')
            if min_v or max_v:
                attr['validate_min'] = min_v or None
                attr['validate_max'] = max_v or None
                attr['validate_min_error'] = '!!Under min value %s' %min_v
                attr['validate_max_error'] = '!!Over max value %s' %max_v
        if attr.get('condition'):
            condition = attr.pop('condition')
            attr['row_hidden'] = """==function(sourceNode){
                                        if(%s){
                                            return false;
                                        }else{
                                            sourceNode.setRelativeData('.%s',null);
                                            return true;
                                        }
                                    }(this);""" %(condition,attr['code'])
            conditionArgs = dict([('row_%s' %str(x),'^.%s' %x) for x in fields.digest('#a.code') if x in condition])
            attr.update(conditionArgs)
            #fb.dataFormula('.%(code)s' %attr,'v',_if=condition,_else='return null',v='=.%(code)s' %attr,**conditionArgs)
            
    