# -*- coding: UTF-8 -*-

# th_office.py
# Created by Francesco Porcari on 2011-04-10.
# Copyright (c) 2011 Softwell. All rights reserved.

from gnr.web.gnrbaseclasses import BaseComponent

class View(BaseComponent):
    def th_struct(self,struct):
        r = struct.view().rows()
        r.fieldcell('date',width='5em')
        r.fieldcell('to',width='5em')
        r.fieldcell('from',width='15em')
        r.fieldcell('cc',width='12em')
        r.fieldcell('bcc',width='5em')
        r.fieldcell('body',width='15em')
        r.fieldcell('subject',width='12em')
        r.fieldcell('account_id',width='15em')
        
        
    def th_order(self):
        return 'date'
        
    def th_query(self):
        return dict(column='to',op='contains',val='',runOnStart=True)
        
class Form(BaseComponent):
    def th_form(self,pane):
        pass