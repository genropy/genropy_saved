# -*- coding: UTF-8 -*-

# th_razza.py
# Created by Filippo Astolfi on 2011-06-13.
# Copyright (c) 2011 Softwell. All rights reserved.

from gnr.web.gnrbaseclasses import BaseComponent

class View(BaseComponent):
    def th_struct(self,struct):
        r = struct.view().rows()
        r.cell('codice', dtype='T', name='!!Codice', width='4em')
        r.fieldcell('nome', width='12em')
        r.fieldcell('ac_base', width='8em')
        r.fieldcell('ab_base', width='5em')
        r.fieldcell('f_base', width='4em')
        r.fieldcell('r_base', width='6em')
        r.fieldcell('ag_base', width='4em')
        r.fieldcell('int_base', width='6em')
        r.fieldcell('vol_base', width='5em')
        r.fieldcell('simp_base', width='5em')
        r.fieldcell('att_base', width='5em')
        r.fieldcell('mov_base', width='6em')
        r.fieldcell('magia_base', width='4em')
        r.fieldcell('fol_base', width='6em')
        
    def th_order(self):
        return 'nome'
        
    def th_query(self):
        return dict(column='nome', op='contains', val='', runOnStart=True)
        
class Form(BaseComponent):
    def th_form(self, form):
        pass