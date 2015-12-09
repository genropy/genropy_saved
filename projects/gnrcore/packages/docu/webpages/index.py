#!/usr/bin/env python
# encoding: utf-8
"""
Created by Softwell on 2008-07-10.
Copyright (c) 2008 Softwell. All rights reserved.
"""
from gnr.core.gnrdecorator import public_method
from gnr.core.gnrbag import Bag

class GnrCustomWebPage(object):
    py_requires='gnrcomponents/externalcall:BaseRpc'

    @public_method
    def rst(self,*args,**kwargs):
        language = kwargs['selected_language'] if 'selected_language' in kwargs else self.locale.split('-')[0]
        language = language.lower()
        doctable = self.db.table('docu.documentation')
        pkey,docbag = doctable.readColumns(columns='$id,$docbag',
                                                    where='$hierarchical_name=:hname',
                                                    hname='/'.join(args))
        
        docbag = Bag(docbag)
        rst = docbag['%s.rst' %language] or docbag['en.rst'] or docbag['it.rst'] or 'To do...'
        rsttable = doctable.dfAsRstTable(pkey)
        if rsttable:
            rst = '%s\n\n%s' %(rst,rsttable) 
        js_script_url= self.site.getStaticUrl('rsrc:common','localiframe.js',nocache=True)

        return self.site.getService('rst2html')(rst,scripts=[js_script_url])
