# -*- coding: UTF-8 -*-

# htable_picker.py
# Created by Francesco Porcari on 2010-09-22.
# Copyright (c) 2010 Softwell. All rights reserved.

"""HPicker test page"""

class GnrCustomWebPage(object):
    py_requires = 'gnrcomponents/testhandler:TestHandlerFull,gnrcomponents/htablehandler:HTablePicker'
    htable = 'base.category'
    related_table = 'base.ct_catalog'
    relation_path = '@category_id.code'

    def test_1_testpicker(self, pane):
        """Picker on htable"""
        fb = pane.formbuilder(cols=1, border_spacing='3px')
        fb.textbox(value='^.codes', lbl='Codes', width='30em')
        fb.button('Show', action='PUBLISH picker_1_open;')
        self.htablePicker(pane, table=self.htable,
                          nodeId='picker_1', datapath='.struct_picker',
                          input_codes='=.#parent.codes',
                          output_codes='.#parent.codes')


    def test_2_testpicker(self, pane):
        """Picker on related table"""
        fb = pane.formbuilder(cols=1, border_spacing='3px')
        fb.textbox(value='^.pkeys', lbl='Related Pkeys', width='30em')
        fb.div(value='^.output_pkeys', lbl='Related Output Pkeys', width='30em', height='20px', background='red')
        fb.button('Show', action='PUBLISH picker_2_open;')

        def struct(struct):
            r = struct.view().rows()
            r.fieldcell('code', name='Code', width='12em')
            r.fieldcell('description', name='Description', width='20em')
            r.fieldcell('rec_type', name='Type', width='4em')

        self.htablePickerOnRelated(pane, table=self.htable,
                                   related_table=self.related_table,
                                   input_pkeys='=.#parent.pkeys',
                                   output_pkeys='.#parent.output_pkeys',
                                   relation_path=self.relation_path,
                                   grid_struct=struct,
                                   condition='$rec_type IN :rec_types',
                                   condition_pars=dict(rec_types=['I', 'P', 'L']),
                                   nodeId='picker_2', datapath='.struct_picker')

    def __test_3_testpicker_bc(self, pane):
        """Picker on bc"""

        bc = pane.borderContainer(height='400px')
        top = bc.contentPane(region='top')
        fb = top.formbuilder(cols=1, border_spacing='3px')
        fb.textbox(value='^.codes', lbl='Codes', width='30em')

        self.htablePicker(bc.contentPane(region='center'), table=self.htable,
                          grid_columns=self.db.table(self.htable).baseViewColumns(),
                          input_codes='=.#parent.codes', output_codes='.#parent.codes',
                          resultpath=None, nodeId='picker_3',

                          datapath='.struct_picker', editMode='bc')

    def __test_4_testpicker_bc(self, pane):
        """Picker on bc"""

        bc = pane.borderContainer(height='400px')
        top = bc.contentPane(region='top')
        fb = top.formbuilder(cols=1, border_spacing='3px')
        fb.textbox(value='^.pkeys', lbl='Related Pkeys', width='30em')
        fb.div(value='^.output_pkeys', lbl='Related Output Pkeys', width='30em', height='20px', background='red')

        self.htablePickerOnRelated(bc.contentPane(region='center'), table=self.htable,
                                   related_table=self.related_table,
                                   input_pkeys='=.#parent.pkeys',
                                   output_pkeys='.#parent.output_pkeys',
                                   relation_path=self.relation_path,
                                   nodeId='picker_4', datapath='.struct_picker', editMode='bc')

                            
                            
