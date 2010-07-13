#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-

#  Created by Giovanni Porcari on 2007-03-24.
#  Copyright (c) 2007 Softwell. All rights reserved.

from gnr.core.gnrbag import Bag

class GnrCustomWebPage(object):
    py_requires='gnrcomponents/dynamicform'
        
    def main(self, root, **kwargs):
        self.dynamicForm(root,nodeId='myform',storepath='contacts',reloader='^gnr.onStart',
                        row_types={'phone':'!!Phone','email':"Email",'fax':'Fax','post_address':'Postal'},
                        type_field='contact_type')
                        
        #data d'esempio
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
        root.data('contacts',egData)
        
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