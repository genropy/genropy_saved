#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#
#  untitled
#
#  Created by Giovanni Porcari on 2007-03-24.
#  Copyright (c) 2007 Softwell. All rights reserved.
#

""" Buttons """
import os
from gnr.core.gnrbag import Bag
from gnr.web.gnrwebpage import GnrWebPage

# --------------------------- GnrWebPage subclass ---------------------------
class GnrCustomWebPage(object):
    
    def main(self, root, **kwargs):
        root = self.rootLayoutContainer(root)
        root.data('record.sex','F')
        #root.data('record.name','John')
        root.data('record.state','CA')
        root.data('record.prov','TO')
        root.data('record.sport','BB')
        root.data('record.phone_tipe','M')
        root.data('values.states',self.tableData_states())
        root.data('values.sex',self.tableData_sex(),id='#k',caption='#v')
        root.dataRemote('values.sport','tableData_sport',id='.pkey',caption='.Description')
        root.data('values.prov',remote='tableData_prov',id='#k',caption='#v')
        root.data('values.phones',self.tableData_phone(),caption='name')
        fb=root.formbuilder(cols="2")
        fb.textbox(lbl='Name',value='^record.name')
        
       #fb.filteringSelect(lbl='State', value = '^record.state',ignoreCase=True,
       #                     storepath='values.states')
       #
       #fb.filteringSelect(lbl='Sex', value = '^record.sex',
       #                      storepath='values.sex',ignoreCase=True)
       #                      
       #fb.filteringSelect(lbl='Phone', value = '^record.phone_tipe',
       #                      storepath='values.phones',ignoreCase=True,
       #                      storecaption='value')
        
        fb.filteringSelect(lbl='Sport', value = '^record.sport',
                              storepath='values.sport',ignoreCase=True)
        
      # fb.filteringSelect(lbl='Province', value = '^record.prov',
      #                       storepath='values.prov',ignoreCase=True)
      # fb.button('Open dialog',action="genro.dialogs.mydialog.show()")  
      # ccc=fb.dropdownButton('Open tooltip dialog')  
      # 
      # dlg=root.dialog(title='this is a dialog',gnrId='dialogs.mydialog',execute="alert('done')")
      # 
      # dx=dlg.formbuilder(cols="1")
      # dx.textbox(lbl='Old password')
      # dx.textbox(lbl='New password')
      # dx.button('confirm')
      # dlg=ccc.tooltipDialog(title='this is a tooltip dialog',execute="alert('done')")
      # dx=dlg.formbuilder(cols="1")
      # dx.textbox(lbl='My password')
      # dx.textbox(lbl='My New password')
      # dx.button('Confirm')
      
    def tableData_states(self):
        mytable=Bag()
        mytable.setItem('r1',None,id='CA',caption='California')
        mytable.setItem('r2',None,id='IL',caption='Illinois')
        mytable.setItem('r3',None,id='NY',caption='New York')
        mytable.setItem('r4',None,id='TX',caption='Texas')
        mytable.setItem('r5',None,id='AL',caption='Alabama')
        return mytable


    def tableData_phone(self):
        mytable=Bag()
        mytable.setItem('r1',None,id='H',name='Home')
        mytable.setItem('r2',None,id='W',name='Work')
        mytable.setItem('r3',None,id='M',name='Mobile')
        mytable.setItem('r4',None,id='F',name='Fax')
        mytable.setItem('r5',None,id='X',name='Others')
        return mytable
    
    def tableData_sex(self):
        mytable=Bag()
        mytable.setItem('M','Male')
        mytable.setItem('F','Female')
        return mytable
    
    def rpc_tableData_sport(self,**kwargs):
        mytable=Bag()
        mytable.setItem('r1.pkey','SC')
        mytable.setItem('r1.Description','Soccer')
        mytable.setItem('r2.pkey','BK')
        mytable.setItem('r2.Description','Basket')
        mytable.setItem('r3.pkey','TE')
        mytable.setItem('r3.Description','Tennis')
        mytable.setItem('r4.pkey','HK')
        mytable.setItem('r4.Description','Hockey')
        mytable.setItem('r5.pkey','BB')
        mytable.setItem('r5.Description','Baseball')
        mytable.setItem('r6.pkey','SB')
        mytable.setItem('r6.Description','Snowboard')
        return mytable
    
    def rpc_tableData_prov(self):
        s = self.db.query('utils.province',columns='$codice,$descrizione',order_by='$codice').selection()
        return Bag(s.output('list',columns='codice,descrizione'))

        
def index(req, **kwargs):
    return GnrWebPage(req, GnrCustomWebPage, __file__, **kwargs).index()