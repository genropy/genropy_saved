# -*- coding: UTF-8 -*-

# th_user.py
# Created by Saverio Porcari on 2011-03-13.
# Copyright (c) 2011 Softwell. All rights reserved.

from gnr.web.gnrbaseclasses import BaseComponent

class View(BaseComponent):
    def th_struct(self,struct):
        r = struct.view().rows()
        r.fieldcell('username',name='Username',width='10em')
        r.fieldcell('fullname',name='Fullname',width='20em')
        r.fieldcell('email',name='Email',width='20em')
        r.fieldcell('@tags.@tag_id.code',name='Tags',width='100%')
        r.fieldcell('auth_tags',name='Old tags',width='15em')
        
        
    def th_order(self):
        return 'username'
        
    def th_query(self):
        return dict(column='username',op='contains', val='')

class Form(BaseComponent):
    def prova(self,pane):
        pass
    def th_form(self, form):
        pane = form.record
        self.prova(pane)
        pane.div('!!Login Data', _class='pbl_roundedGroupLabel')
        fb = pane.div(margin='5px').formbuilder(cols=2, border_spacing='6px',width='100%',fld_width='100%')
        fb.field('firstname',lbl='!!Firstname')
        fb.field('username',lbl='!!Username',validate_nodup=True,validate_notnull_error='!!Existing')
        fb.field('lastname',lbl='!!Lastname')
        
        fb.textBox(value='^.md5pwd', lbl='Password', type='password',validate_notnull=True, validate_notnull_error='!!Required')
        fb.field('status', tag='filteringSelect', values='!!conf:Confirmed,wait:Waiting', 
                 validate_notnull=True, validate_notnull_error='!!Required')
        fb.field('email', lbl='!!Email')

