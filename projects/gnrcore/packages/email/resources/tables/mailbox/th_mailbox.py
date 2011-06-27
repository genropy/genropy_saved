# -*- coding: UTF-8 -*-

# th_office.py
# Created by Francesco Porcari on 2011-04-10.
# Copyright (c) 2011 Softwell. All rights reserved.

from gnr.web.gnrbaseclasses import BaseComponent

class View(BaseComponent):
    def th_struct(self,struct):
        r = struct.view().rows()
        r.fieldcell('code',width='5em')
        r.fieldcell('direction',width='15em')
        r.fieldcell('description',width='12em')
        
    def th_order(self):
        return 'protocol'
        
    def th_query(self):
        return dict(column='code',op='contains',val='',runOnStart=True)
        
class Form(BaseComponent):
    def th_form(self,pane):
        pass