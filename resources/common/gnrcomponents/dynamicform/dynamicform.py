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

class DynamicForm(BaseComponent):
    py_requires='gnrcomponents/framegrid:FrameGrid,gnrcomponents/htablehandler:HTableHandlerBase'
    
    @struct_method
    def df_fieldsGrid(self,pane,storepath=None,standard_range=False,title=None,**kwargs):   
        def struct(struct):
            r = struct.view().rows()
            r.cell('_row_count',hidden=True,counter=True)
            r.cell('code', name='!!Code', width='5em')
            r.cell('description', name='!!Description', width='15em')
            r.cell('field_type', name='!!Type', width='10em')
        
            r.cell('field_source', name='!!Source', width='10em')
            r.cell('range', name='!!Min:Max',width='5em')
            #r.cell('max', name='!!Max',dtype='N', width='5em')
            if standard_range:
                r.cell('standard_range', name='Std.Range', width='10em')
            r.cell('formula', name='!!Formula', width='15em') 
            r.cell('condition', name='!!Condition',width='10em')  
 
            r.checkboxcell('do_summary', name='!!Summary',width='6em')       
            r.checkboxcell('mandatory', name='!!Mandatory',width='7em')  

            
        frame = pane.frameGrid(storepath=storepath,struct=struct,datamode='bag',datapath='#FORM.fieldsGrid_%i' %id(pane),
                              grid_selfDragRows=True,**kwargs)
        ge = frame.grid.gridEditor()
        ge.textbox(gridcell='code')
        ge.textbox(gridcell='description')
        ge.filteringSelect(gridcell='field_type',values='!!T:Text,TL:Long Text,L:Integer,N:Decimal,D:Date,B:Boolean,H:Time')
        ge.textbox(gridcell='field_source')
        ge.textbox(gridcell='range')
        if standard_range:      
            ge.textbox(gridcell='standard_range')
        ge.textbox(gridcell='formula')
        ge.textbox(gridcell='condition')
        frame.top.slotToolbar('3,vtitle,*,delrow,addrow,2',vtitle=title or '!!Fields',delrow_parentForm=True,addrow_parentForm=True)
        return frame 
    @struct_method
    def df_dynamicFieldsPane(self,pane,df_table=None,df_pkey=None,df_folders=None,**kwargs):
        pane.div().remote(self.df_remoteDynamicForm,df_table=df_table,df_pkey=df_pkey,
                    df_folders=df_folders,
                    **kwargs)

    
    @public_method
    def df_remoteDynamicForm(self,pane,df_table=None,df_pkey=None,df_folders=None,datapath=None,**kwargs):
        if not df_pkey:
            pane.div('!!No Form descriptor')
            return
        dbstore_kwargs = dictExtract(kwargs,'dbstore_',pop=True)
        pane.attributes.update(kwargs)
        df_tblobj = self.db.table(df_table)
        formDescriptor = df_tblobj.getFormDescriptor(pkey=df_pkey,folders=df_folders)
        fields = formDescriptor[df_tblobj.attributes.get('df_fields','fields')]
        fielddict = {'T':'Textbox','L':'NumberTextBox','D':'DateTextBox','B':'Checkbox','N':'NumberTextBox', 'TL':'Simpletextarea'}
        fb = pane.div(margin_right='10px').formbuilder(cols=1,datapath=datapath)
        for fnode in fields:
            attr = dict(fnode.attr)
            field_type = attr.pop('field_type')
            attr['tag'] = fielddict[field_type]
            #attr['colspan'] = col_max if field_type == 'TL' else 1
            self._df_handleFieldSource(attr,dbstore_kwargs=dbstore_kwargs)
            self._df_handleFieldFormula(attr,fb=fb,fields=fields)
            self._df_handleFieldValidation(attr,fb,fields=fields)
            if field_type=='TL':
                attr['lbl_vertical_align'] = 'top'
            fb.child(value='^.%s' %attr.pop('code'), lbl='%s' %attr.pop('description',''),**attr)
                    
    def _df_handleFieldSource(self,attr,dbstore_kwargs=None): #dbstore_name='@pratica_id.@condominio_id.dbstore' ,dbstore_pkg='cond'
        field_source = attr.pop('field_source',None)
        if not field_source:
            return
        if '.' in field_source:
            tag = 'dbSelect'
            attr['dbtable'] = field_source
            htbl = hasattr(self.db.table(field_source),'htableFields')
            pkg,tblname = field_source.split('.')
            attr['hasDownArrow'] =True
            if pkg in dbstore_kwargs.get('pkg','').split(','):
                attr['_storename'] = '=%(name)s' %dbstore_kwargs
        else:
            if ':' in field_source:
                tag = 'FilteringSelect'
            else:
                tag = 'ComboBox'
            attr['values'] = field_source
        attr['tag'] = tag
        
    def _df_handleFieldFormula(self,attr,fb,fields=None):
        formula = attr.pop('formula',None)
        if not formula:
            return
        formulaArgs = dict([(str(x),'^.%s' %x) for x in fields.digest('#a.code') if x in formula])
        fb.dataFormula(".%s" %attr['code'], formula,**formulaArgs)
        attr['readOnly'] =True 
    
    def _df_handleFieldValidation(self,attr,fb,fields):
        if 'range' in attr:
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
            
    