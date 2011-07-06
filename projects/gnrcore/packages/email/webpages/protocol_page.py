# -*- coding: UTF-8 -*-

# office_page.py
# Created by Saverio Porcari on 2011-04-08.
# Copyright (c) 2011 __MyCompanyName__. All rights reserved.

class GnrCustomWebPage(object):
    py_requires = """public:TableHandlerMain"""
    maintable = 'email.protocol'

    def windowTitle(self):
        return '!!Protocols'

    def pageAuthTags(self, method=None, **kwargs):
        return 'user'

    def tableWriteTags(self):
        return 'user'

    def tableDeleteTags(self):
        return 'user'

    def barTitle(self):
        return '!!Protocols'
    
    def th_form(self,form,**kwargs):
        form_center = form.record
        
        fb = form_center.formbuilder(cols=2, width='350px', margin_left='.5em', border_spacing='3px', margin_top='.5em',
                              lbl_width='8em',tdl_width='8em', fld_width='100%')

        fb.field('code', width='10em', colspan=2)
        fb.filteringSelect(value='^.direction', values='!!I:In,O:Out,B:Both',lbl='!!Direction', colspan=2)
        fb.field('description', colspan=2)
        