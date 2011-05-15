# -*- coding: UTF-8 -*-

# th_user.py
# Created by Saverio Porcari on 2011-03-13.
# Copyright (c) 2011 Softwell. All rights reserved.

from gnr.web.gnrbaseclasses import BaseComponent

class ViewFromUser(BaseComponent):
    def th_struct(self,struct):
        r = struct.view().rows()
        r.fieldcell('tag_code',name='Tag',width='10em')
        r.fieldcell('tag_description',name='Description',width='20em')
        r.fieldcell('tag_note',name='Notes',width='100%')
        
    def th_order(self):
        return 'tag_code'
        
    def th_query(self):
        return dict(column='tag_code',op='contains', val='%')