# -*- coding: UTF-8 -*-

# testcomponent.py
# Created by Francesco Porcari on 2010-09-22.
# Copyright (c) 2010 Softwell. All rights reserved.

"""HPicker test page"""

class GnrCustomWebPage(object):
    py_requires='gnrcomponents/testhandler:TestHandlerFull,gnrcomponents/htablehandler:HTablePicker'
    
    htable = 'base.category'
    grid_table = 'base.pr_product'
    grid_where = '@category_id.code IN :codes'
    
    def test_1_testpicker(self,pane):
        """Picker on htable"""
        fb = pane.formbuilder(cols=1, border_spacing='3px')
        fb.textbox(value='^.codes',lbl='Codes')
        fb.button('Show',action='PUBLISH picker_1_open;')
        self.htablePicker(pane,table=self.htable, 
                            nodeId='picker_1',datapath='.struct_picker',
                            input_codes='=.#parent.codes',
                            onAccept='console.log(pkeys); console.log(codes);',
                            onChange='console.log(pkeys); console.log(codes);',
                            dialogPars=dict(width='600px'))
    
    def __test_2_testpicker(self,pane):
        """Picker on related table"""
        pane.button('Show',fire='.struct_picker.open')
        self.htablePicker(pane,table=self.htable,
                            grid_columns=self.db.table(self.grid_table).baseViewColumns(),
                            grid_where=self.grid_where,grid_table=self.grid_table,
                            resultpath=None,nodeId='struct_picker2',datapath='.struct_picker',
                            dialogPars=dict(width='600px'))
                            
    def __test_3_testpicker(self,pane):
        fb = pane.formbuilder(cols=1, border_spacing='3px')
        fb.textbox(value='^.codes',lbl='Codes')
        fb.button('Show',fire='.struct_picker.open')
        
        self.htablePicker(pane,table=self.htable,
                            grid_columns=self.db.table(self.htable).baseViewColumns(),
                            input_codes='=.#parent.codes',
                            resultpath=None,nodeId='struct_picker',datapath='.struct_picker',
                            dialogPars=dict(width='600px'))
                            


    def __test_4_testpicker(self,pane):
        """Picker on related table"""
        pane.button('Show',fire='.struct_picker.open')
        
        
        self.htablePicker(pane,table=self.htable,column='id', 
                            grid_columns=self.db.table(self.grid_table).baseViewColumns(),
                            grid_where=self.grid_where,grid_table=self.grid_table,
                            input_pkeys='=',
                            onAccept='console.log(pkeys); console.log(codes);',
                            onChange='console.log(pkeys); console.log(codes);',
                            nodeId='struct_picker2',datapath='.struct_picker',
                            dialogPars=dict(width='600px'))
                            
                            
                            
                            
