#!/usr/bin/python
# -*- coding: utf-8 -*-

from gnr.web.gnrbaseclasses import BaseComponent
from gnr.core.gnrdecorator import public_method

class View(BaseComponent):

    def th_struct(self,struct):
        r = struct.view().rows()
        r.fieldcell('item_id')
        r.fieldcell('category_id')
        r.fieldcell('url', hidden=True)
        r.cell('apri_tab', name="Apri", calculated=True, width='3em',
               cellClasses='cellbutton',
               format_buttonclass='icnBaseLens buttonIcon',
               format_isbutton=True, format_onclick="""var row = this.widget.rowByIndex($1.rowIndex);
                                                           genro.childBrowserTab(row['url']);""")

    def th_order(self):
        return 'item_id'

    def th_query(self):
        return dict(column='item_id', op='contains', val='')



class Form(BaseComponent):

    def th_form(self, form):
        pane = form.record
        fb = pane.formbuilder(cols=2, border_spacing='4px')
        fb.field('item_id')
        fb.field('category_id')


    def th_options(self):
        return dict(dialog_height='400px', dialog_width='600px')
