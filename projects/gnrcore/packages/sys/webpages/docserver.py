#!/usr/bin/env python
# encoding: utf-8
"""
Created by Softwell on 2008-07-10.
Copyright (c) 2008 Softwell. All rights reserved.
"""
from builtins import object
from gnr.core.gnrdecorator import public_method
LAGUAGES = ('it','en')

class GnrCustomWebPage(object):
    py_requires='gnrcomponents/externalcall:BaseRpc'

    @public_method
    def rst(self,*args,**kwargs):
        language = self.locale.split('-')[0]
        doctable = self.db.table('.'.join(args[0:2]))
        urlist = args[2:]
        columns = '$id,$content_rst_it,$content_rst_en' if language == 'it' else '$id,$content_rst_en,$content_rst_it'
        pkey,rst,alt_rst = doctable.readColumns(columns=columns,
                                                    where='$hierarchical_name=:hname',
                                                    hname='/'.join(urlist))
        rst = rst or alt_rst or 'To do...'
        if hasattr(doctable,'dfAsTable'):
            rsttable = doctable.dfAsTable(pkey)
            if rsttable:
               rst = '%s\n\n%s' %(rst,rsttable) 
        return self.site.getService('rst2html')(rst)