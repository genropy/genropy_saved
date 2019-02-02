#!/usr/bin/env python
# encoding: utf-8
"""
Created by Softwell on 2008-07-10.
Copyright (c) 2008 Softwell. All rights reserved.
"""
from builtins import object
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

            rst = '%s\n\n**Parameters:**\n\n%s' %(rst,rsttable) 
        js_script_url= self.site.getStaticUrl('rsrc:common','localiframe.js',nocache=True)

        return self.site.getService('rst2html')(rst,scripts=[js_script_url])


    @public_method
    def search(self,text=None,**kwargs):
        language = kwargs['selected_language'] if 'selected_language' in kwargs else self.locale.split('-')[0]
        language = language.lower()
        doctable = self.db.table('docu.documentation')
        f = doctable.query(where="$is_published IS TRUE AND ( $title_%s ILIKE :val OR $rst_%s ILIKE :val ) AND $title_%s IS NOT NULL" %(language,language,language),val='%%%s%%' %text,
                        columns='$hierarchical_name,$rst_%s AS rst,$title_%s AS title' %(language,language)).fetch()
        tpl = '`%(title)s (%(hierarchical_name)s) <%(url)s>`_'
        result = []
        for r in f:
            result.append(tpl %dict(title=r['title'],hierarchical_name=r['hierarchical_name'],url='/docu/index/rst/%s' %r['hierarchical_name']))
        result = '\n\n'.join(result)
        return self.site.getService('rst2html')(result)

