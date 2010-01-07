#!/usr/bin/env python
# encoding: utf-8
"""
etcf.py

Created by Jeff B. Edwards on 2008-11-07.
Copyright (c) 2008 Goodsoftware Pty Ltd All rights reserved.
"""
import os
from gnr.core.gnrbag import Bag

class GnrCustomWebPage(object):
    maintable='mnt.jos_usertrace'
    py_requires='public:Public,standard_tables:TableHandler,public:IncludedView'

    def windowTitle(self):
        return '!!Accessi'

    def pageAuthTags(self, method=None, **kwargs):
        return 'admin'
        
    def tableWriteTags(self):
        return 'admin'
        
    def tableDeleteTags(self):
        return 'admin'
        
    def barTitle(self):
        return '!!Accessi'
        
    def columnsBase(self,):
        return """
                  id/Id:4,
                  username/Nome Utente:14,
                  userip/IP:14,
                  useragent:14,
                  userurl:14,
                  userreferer:12,
                  date:8,
                  time:7
               """
    #           look to this url for info on formatting   http://www.unicode.org/reports/tr35/tr35-4.html#Date_Format_Patterns

    def formBase(self, parentBC,  disabled=False, **kwargs):
        bc=parentBC.borderContainer(**kwargs)
        base= bc.contentPane(region='center', _class='pbl_roundedGroup',margin='5px')
        base.div('!!Dati',_class='pbl_roundedGroupLabel')
        fb = base.formbuilder(cols=1, margin_left='2em',border_spacing='7px',margin_top='1em',disabled=disabled)
        fb.field('mnt.jos_usertrace.id',width='5em')
        fb.field('mnt.jos_usertrace.username',width='24em')

    def orderBase(self):
        return 'username'
    
    def queryBase(self):
        return dict(column='username',op='contains', val='%', runOnStart=False)

                               
