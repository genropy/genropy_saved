# -*- coding: UTF-8 -*-

# th_office.py
# Created by Francesco Porcari on 2011-04-10.
# Copyright (c) 2011 Softwell. All rights reserved.

from gnr.web.gnrbaseclasses import BaseComponent

class View(BaseComponent):
    def th_struct(self,struct):
        r = struct.view().rows()
        r.fieldcell('title',width='5em')
        r.fieldcell('mime_type',width='15em')
        r.fieldcell('size',width='12em')
        r.fieldcell('path',width='5em')
        r.fieldcell('message_id',width='15em')
        
    def th_order(self):
        return 'title'
        
    def th_query(self):
        return dict(column='title',op='contains',val='',runOnStart=True)
        
class Form(BaseComponent):
    def th_form(self,pane):
        pass