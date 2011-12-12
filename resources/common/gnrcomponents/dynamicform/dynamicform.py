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
    py_requires='gnrcomponents/framegrid:FrameGrid'
    
    @struct_method
    def df_fieldsGrid(self,pane,storepath=None,standard_range=False,title=None,**kwargs):   
        def struct(struct):
            r = struct.view().rows()
            r.cell('code', name='!!Code', width='5em')
            r.cell('description', name='!!Description', width='15em')
            r.cell('field_type', name='!!Type', width='10em')
        
            r.cell('field_source', name='!!Source', width='10em')
            r.cell('range', name='!!Min:Max',width='10em')
            #r.cell('max', name='!!Max',dtype='N', width='5em')
            if standard_range:
                r.cell('standard_range', name='Std.Range', width='10em')
            r.cell('formula', name='!!Formula', width='10em')  
            r.checkboxcell('do_summary', name='!!Summary',width='6em')       
            r.checkboxcell('mandatory', name='!!Mandatory',width='7em')  
            
        frame = pane.frameGrid(storepath=storepath,struct=struct,datamode='bag',datapath='#FORM.fieldsGrid_%i' %id(pane),**kwargs)
        ge = frame.grid.gridEditor()
        ge.textbox(gridcell='code')
        ge.textbox(gridcell='description')
        ge.filteringSelect(gridcell='field_type',values='!!T:Text,TL:Long Text,L:Integer,N:Decimal,D:Date,B:Boolean,H:Time')
        ge.textbox(gridcell='field_source')
        ge.textbox(gridcell='range')
        if standard_range:      
            ge.textbox(gridcell='standard_range')
        ge.textbox(gridcell='formula')
        frame.top.slotToolbar('3,gridtitle,*,delrow,addrow,2',gridtitle=title or '!!Fields',delrow_parentForm=True,addrow_parentForm=True)
        return frame 
    @struct_method
    def df_dynamicFieldsPane(self,pane,df_table=None,df_pkey=None,df_folders=None,**kwargs):
        pane.remote(self.df_remoteDynamicForm,df_table=df_table,df_pkey=df_pkey,
                    df_folders=df_folders,
                    **kwargs)

    
    @public_method
    def df_remoteDynamicForm(self,pane,df_table=None,df_pkey=None,df_folders=None,datapath=None,**kwargs):
        if not df_pkey:
            pane.div('!!No Form descriptor')
            return
        fb_kwargs = dictExtract(kwargs,'fb_',pop=True)
        dbstore_kwargs = dictExtract(kwargs,'dbstore_',pop=True)
        pane.attributes.update(kwargs)
        df_tblobj = self.db.table(df_table)
        formDescriptor = df_tblobj.getFormDescriptor(pkey=df_pkey,folders=df_folders)
        fields = formDescriptor[df_tblobj.attributes.get('df_fields','fields')]
        fb_kwargs.setdefault('datapath',datapath)
        fielddict = {'T':'Textbox','L':'NumberTextBox','D':'DateTextBox','B':'Checkbox','N':'NumberTextBox', 'TL':'Simpletextarea'}
        fb = pane.formbuilder(**fb_kwargs)
        for fnode in fields:
            attr = dict(fnode.attr)
            field_type = attr.pop('field_type')
            attr['tag'] = fielddict[field_type]
            attr['colspan'] = 2 if field_type == 'TL' else 1
            self._df_handleFieldSource(attr,dbstore_kwargs=dbstore_kwargs)
            self._df_handleFieldFormula(attr,fb=fb,fields=fields)
            fb.child(value='^.%s' %attr.pop('code'), lbl='%s' %attr.pop('description'),**attr)
        
    def _df_handleFieldSource(self,attr,dbstore_kwargs=None):
        field_source = attr.pop('field_source',None)
        if not field_source:
            return
        if '.' in field_source:
            tag = 'dbSelect'
            attr['dbtable'] = field_source
            pkg,tblname = field_source.split('.')
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
        #formula = re.sub('[^\s,()*/%+-]+',lambda v:  v.group(0).replace(',','.') if v.group(0).startswith('Math.')else 'parseFloat(%s)' % v.group(0).replace(',','.'),formula)                                                        
        #re.sub('[^\s()*/%+-]+',lambda v: 'parseFloat(%s)' % v.group(0),formula)
        #print bazinga
        fb.dataFormula(".%s" %attr['code'], formula,**formulaArgs)
        attr['readOnly'] =True 
    
    
    