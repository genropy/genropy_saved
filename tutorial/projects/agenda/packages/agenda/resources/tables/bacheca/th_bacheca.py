# -*- coding: UTF-8 -*-

# th_bacheca.py
# Created by Filippo Astolfi on 2011-04-07.
# Copyright (c) 2011 Softwell. All rights reserved.

from gnr.web.gnrbaseclasses import BaseComponent
import datetime

class View(BaseComponent):
    def th_struct(self,struct):
        r = struct.view().rows()
        r.fieldcell(field='giorno', width='5%')
        r.fieldcell('ora', width='5%')
        r.fieldcell('autore', width='10%')
        r.fieldcell('titolo', width='20%')
        r.fieldcell('contenuto', width='60%')
        
    def th_order(self):
        return 'giorno'
        
    def th_query(self):
        return dict(column='giorno', op='', val='', runOnStart=True)
        
class Form(BaseComponent):
    py_requires = """public:Public,tablehandler/th_main:TableHandler,
                     foundation/macrowidgets:RichTextEditor"""

    def th_form(self, form):
        pane = form.record
        bc = pane.borderContainer()
        pane = bc.contentPane(region='top')
        center = bc.borderContainer(region='center')
        fb = pane.formbuilder(cols=2, border_spacing='6px', fld_width='20em')
        fb.field('giorno', readOnly=True, width='6em')
        fb.field('ora', readOnly=True, width='4em')
        fb.field('autore', readOnly=True, width='12em')
        fb.field('titolo', width='12em')
        self.RichTextEditor(center,
                            value='^.contenuto',
                            config_uiColor='#68858E',
                            config_toolbarStartupExpanded=True,
                            config_height='430px',
                            toolbar='standard')
                            
    def onLoading(self, record, newrecord, loadingParameters, recInfo):
        if newrecord:
            record['autore'] = self.user
            record['giorno'] = self.workdate
            record['ora'] = datetime.datetime.now().time()