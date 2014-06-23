# -*- coding: UTF-8 -*-

# office_page.py
# Created by Saverio Porcari on 2011-04-08.
# Copyright (c) 2011 __MyCompanyName__. All rights reserved.

class GnrCustomWebPage(object):
    py_requires = """public:TableHandlerMain"""
    maintable = 'email.account'

    def windowTitle(self):
        return '!!Account'

    def pageAuthTags(self, method=None, **kwargs):
        return 'user'

    def tableWriteTags(self):
        return 'user'

    def tableDeleteTags(self):
        return 'user'

    def barTitle(self):
        return '!!Account'
    
    def th_form(self,form,**kwargs):
        form_center = form.center
        
        fb = form_center.formbuilder(cols=2, width='350px', margin_left='.5em', border_spacing='3px', margin_top='.5em',
                              lbl_width='8em',tdl_width='8em', fld_width='100%')

        fb.field('account_name', colspan=2)
        fb.field('full_name', colspan=2)
        fb.field('host')
        fb.field('port')
        fb.field('protocol_code')
        fb.field('tls')
        fb.field('ssl')
        fb.field('username')
        fb.textBox(value='^.password', lbl='Password', type='password')