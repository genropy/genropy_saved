# -*- coding: UTF-8 -*-

# th_office.py
# Created by Francesco Porcari on 2011-04-10.
# Copyright (c) 2011 Softwell. All rights reserved.

from gnr.web.gnrbaseclasses import BaseComponent

class View(BaseComponent):
    def th_struct(self,struct):
        r = struct.view().rows()
        r.fieldcell('account_name',width='5em')
        r.fieldcell('full_name',width='15em')
        r.fieldcell('username',width='15em')
        r.fieldcell('host',width='12em')
        r.fieldcell('port',width='5em')
        r.fieldcell('protocol_code',width='5em')
        r.fieldcell('tls',width='3em')
        r.fieldcell('ssl',width='3em')
        
    def th_order(self):
        return 'account_name'
        
    def th_query(self):
        return dict(column='account_name',op='contains',val='',runOnStart=True)
        
class Form(BaseComponent):
    def th_form(self,pane):
        pass