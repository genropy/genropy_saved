# -*- coding: UTF-8 -*-

# dynamicform.py
# Created by Francesco Porcari on 2010-12-27.
# Copyright (c) 2010 Softwell. All rights reserved.

"Test page description"
from gnr.core.gnrbag import Bag

class GnrCustomWebPage(object):
    py_requires="gnrcomponents/testhandler:TestHandlerFull,gnrcomponents/dynamicform"

    def windowTitle(self):
        return 'Dynamic form'
         
    def test_0_data(self,pane):
        egData = Bag()
        egData['r_1.contact_type'] = 'phone'
        egData['r_1.location'] = 'Work'
        egData['r_1.content'] = '44422444'
        
        egData['r_2.contact_type'] = 'email'
        egData['r_2.content'] = 'jeffedwa@goodsoftware.com'
        
        egData['r_3.contact_type'] = 'post_address'
        egData['r_3.suburb'] = 'Sydney'
        egData['r_3.state'] = 'NSW' #thanks
        egData['r_3.address'] =  '1 Lucinda Ave'
        pane.data('data',egData)
        
    def test_1_dynamicform(self,pane):
        """Dinamycform"""        
        self.dynamicForm(pane,nodeId='myform',storepath='contacts',reloader='^gnr.onStart',
                        row_types={'phone':'!!Phone','email':"Email",'fax':'Fax','post_address':'Postal'},
                        type_field='contact_type')
                                
        
    def myform_row(self,row,disabled=None,**kwargs):
        #inside remote
        fb = row.formbuilder(cols=2, border_spacing='2px',disabled=disabled)
        fb.combobox(value='^.location',values='Home,Work,Main',lbl='Loc.')
        fb.textbox(value='^.content')
        
    def myform_email_row(self,row,disabled=None,**kwargs):
        fb = row.formbuilder(cols=1, border_spacing='2px',disabled=disabled)
        fb.textbox(value='^.content',lbl='Url')
        
    def myform_post_address_row(self,row,disabled=None,**kwargs):
        fb = row.formbuilder(cols=2, border_spacing='2px',disabled=disabled)
        fb.textbox(value='^.suburb',lbl='Suburb',width='12em')
        fb.textbox(value='^.state',lbl='State',width='3em')
        fb.simpleTextArea(value='^.address',colspan=2,width='100%')