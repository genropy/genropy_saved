#!/usr/bin/python
# -*- coding: UTF-8 -*-

from gnr.web.gnrbaseclasses import BaseComponent
from gnr.core.gnrdecorator import public_method

class View(BaseComponent):

    def th_struct(self,struct):
        r = struct.view().rows()
        r.fieldcell('codekey')
        r.fieldcell('code')
        r.fieldcell('pkg')
        r.fieldcell('tbl')
        r.fieldcell('fld')
        r.fieldcell('counter')
        r.fieldcell('last_used')

    def th_order(self):
        return 'tbl'

    def th_query(self):
        return dict(column='tbl', op='contains', val='')



class Form(BaseComponent):

    def th_form(self, form):
        bc = form.center.borderContainer()
        fb = bc.contentPane(region='top',datapath='.record').formbuilder(cols=2, border_spacing='4px')
        fb.field('codekey')
        fb.field('code')
        fb.field('pkg')
        fb.field('tbl')
        fb.field('fld')
        fb.field('counter')
        fb.field('last_used')
        tc = bc.tabContainer(region='center',margin='2px')
        tc.contentPane(title='Holes').bagGrid(storepath='#FORM.record.holes',struct=self.holesStruct,
                        pbl_classes=True,title='Holes', margin='2px',addrow=False,delrow=False)
        tc.contentPane(title='Duplicates')
        tc.contentPane(title='Wrong order')

    def holesStruct(self,struct):
        r = struct.view().rows()
        r.cell('cnt_from', name='Counter from',dtype='L', width='10em')
        r.cell('cnt_to', name='Counter to',dtype='L', width='10em')
        r.cell('date_from', name='Valid from',dtype='D', width='10em')
        r.cell('date_to', name='Valid to',dtype='D', width='10em')




    def th_options(self):
        return dict(dialog_height='400px', dialog_width='600px')
