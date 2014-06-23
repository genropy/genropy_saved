# -*- coding: UTF-8 -*-

# th_user.py
# Created by Saverio Porcari on 2011-03-13.
# Copyright (c) 2011 Softwell. All rights reserved.

from gnr.web.gnrbaseclasses import BaseComponent

class View(BaseComponent):
    def th_struct(self,struct):
        r = struct.view().rows()
        r.fieldcell('maintable', name='!!Name', width='20em')
        r.fieldcell('name', name='!!Name', width='20em')
        r.fieldcell('username', name='!!Username', width='10em')
        r.fieldcell('version', name='!!Version', width='20em')
        
        
    def th_order(self):
        return 'maintable'
        
    def th_query(self):
        return dict(column='maintable',op='contains', val='')

class Form(BaseComponent):
    pass
    
        
                          
