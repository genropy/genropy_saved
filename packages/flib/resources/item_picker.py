# -*- coding: UTF-8 -*-

# item_uploader.py
# Created by Saverio Porcari on 2010-10-15.
# Copyright (c) 2010 __MyCompanyName__. All rights reserved.

from gnr.web.gnrwebpage import BaseComponent

class FlibPicker(BaseComponent):
    py_requires="""gnrcomponents/htablehandler:HTablePicker"""
    def flibPicker(self,pane,pickerId=None,datapath=None,rootpath=None,
                  current_items=None,selected_items=None,editMode=None):
        """"""
        def item_struct(struct):
            r = struct.view().rows()
            r.fieldcell('__ins_ts', name='!!Inserted on', width='8em')
            r.fieldcell('title', name='!!Title', width='8em')
            r.fieldcell('description', name='!!Description', width='18em')
            r.fieldcell('username', name='!!User', width='8em')
            
        
        self.htablePickerOnRelated(pane,nodeId= pickerId or 'flib_picker',
                                table='flib.category',datapath=datapath,rootpath=rootpath,
                                related_table='flib.item',
                                input_pkeys=current_items,grid_struct=item_struct,
                                grid_filter='title,description,username',
                                output_pkeys=selected_items,
                                relation_path='@flib_item_category_item_id.@category_id.code',editMode=editMode)
    