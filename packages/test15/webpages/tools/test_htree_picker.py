# -*- coding: UTF-8 -*-

# testcomponent.py
# Created by Francesco Porcari on 2010-09-22.
# Copyright (c) 2010 Softwell. All rights reserved.

"""HPicker test page"""

class GnrCustomWebPage(object):
    py_requires='gnrcomponents/testhandler:TestHandlerFull,gnrcomponents/htablehandler:HTablePicker'
    
    htable = 'base.category'
    grid_table = 'base.pt_product'
    grid_where = '$category_code IN :codes'
    
    def test_1_testpicker(self,pane):
        """Picker on htable"""
        pane.button('Show',fire='#struct_picker_dlg.open')
        self.htablePicker(pane,table=self.htable,column='id', 
                            grid_columns=self.db.table(self.grid_table).baseViewColumns(),
                            grid_where=self.grid_where,grid_table=self.grid_table,
                            resultpath=None,nodeId='struct_picker',datapath='.struct_picker',dialogPars=dict(width='400px'))