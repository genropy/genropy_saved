#!/usr/bin/env python
# encoding: utf-8
"""
th.py

Created by Francesco Porcari on 2011-04-28.
Copyright (c) 2011 Softwell. All rights reserved.
"""

from gnr.web.gnrbaseclasses import BaseClasses

class BaseView(BaseClasses):
    def th_struct(self,struct):
        r = struct.view().rows()
        self.th_columns(r)
        
    def th_columns(self,r):
        """
            r.fieldcell('col1', name='Col1',width='10em')
            r.fieldcell('col2', name='Col2',width='100%')
        """
        pass

    def th_order(self):
        "return 'fieldname,..'"
        return
        
    def th_query(self):
        #rename as th_default_query
        """return dict(column='xxx',op='contains',val='')"""
        return         
    
    def th_condition(self):
        """return dict()"""
        return
        
    def th_options(self):
        return dict()
        
class BaseForm(BaseClasses):
    def th_form(self, form):
        pass
    
    def th_dialog(self):
        """return dict()"""
        return

class BaseLinker(BaseClasses):
    def th_options(self):
        return dict(columns=None,#columns for the query
                    auxColumns=None
                        )