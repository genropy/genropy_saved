#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#
#  untitled
#
#  Created by Giovanni Porcari on 2007-03-24.
#  Copyright (c) 2007 Softwell. All rights reserved.
#

""" GnrDojo Hello World """
import os

import datetime
from gnr.core.gnrbag import Bag, DirectoryResolver

# --------------------------- GnrWebPage subclass ---------------------------
class GnrCustomWebPage(object):
    def main(self, root, **kwargs):
        root = self.rootLayoutContainer(root)
        root.data('values.states', self.tableData_states())
        root.data('values.sex', self.tableData_sex(), id='#k', caption='#v')
        root.data('records', self.myRecords())
        fb = root.formbuilder(cols='5', datapath='records',
                              cellspacing='10', background_color='silver', margin='30px', rowdatapath=True)
        for r in range (4):
            self.makeRow(fb,r)
            
        fb.div()
        fb.numberTextBox(value='^totQt',script_init=True,lbl='tot Qt', script="return recs.sum('qt')", script_recs='^records')
        fb.div()
        fb.numberTextBox(value='^totVal',script_init=True,lbl='tot Val', script="return recs.sum('val')", script_recs='^records')

    def makeRow__(self,fb,r): 
        row=fb.row(datapath='.r_%i' % r,_class='xyz')
        name = row.textBox(lbl='Name', value='^.name')
        age = row.numberSpinner(lbl='Age', value='^.age' % r)
        sex = row.filteringSelect(lbl='Sex', value='^.sex' % r,storepath='values.sex')
        state = row.filteringSelect(lbl='State', value = '^.state' % r, storepath='values.states')
    
    def makeRow(self,fb,r): 
        name = fb.textBox(lbl='Name', value='^.name' )
        #age=fb.numberTextBox(lbl='Age', value='.r%i.age' % r)
        age = fb.numberTextBox(lbl='Qt', value='^.qt' )
        age = fb.numberTextBox(lbl='Prezzo', value='^.pr')
        age = fb.numberTextBox(lbl='Valore', value='^.val', disabled=True, 
                           script="return prezzo * qt", script_if='prezzo && qt', script_else='return -1',
                           script_prezzo='^.pr', script_qt='^.qt')
        age = fb.numberTextBox(lbl='Valore', value='^.val2', disabled=True, 
                           script_rpc="calcValore", script_if='prezzo && qt', script_else='return -1',
                           script_prezzo='^.pr', script_qt='^.qt')
        
    def rpc_calcValore(self, prezzo,qt):
        return prezzo * qt
        
    def myRecords(self):
        data=Bag()
        data['r_0.name']='John'
        data['r_0.qt']=26
        data['r_0.pr']=10.3
        data['r_0.val']=10.3 * 26
        data['r_1.name']='Mary'
        data['r_1.qt']=10
        data['r_1.pr']=22.3
        data['r_1.val']=22.3 * 10
        return data
        
    def tableData_sex(self):
        mytable=Bag()
        mytable.setItem('M','Male')
        mytable.setItem('F','Female')
        return mytable
        
    def tableData_states(self):
        mytable=Bag()
        mytable.setItem('r1',None,id='CA',caption='California')
        mytable.setItem('r2',None,id='IL',caption='Illinois')
        mytable.setItem('r3',None,id='NY',caption='New York')
        mytable.setItem('r4',None,id='TX',caption='Texas')
        mytable.setItem('r5',None,id='AL',caption='Alabama')        
        return mytable
    
def index(req, **kwargs):
    return GnrWebPage(req, GnrCustomWebPage, __file__, **kwargs).index()
