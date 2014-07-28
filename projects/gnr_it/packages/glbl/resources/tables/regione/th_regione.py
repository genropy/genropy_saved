# -*- coding: UTF-8 -*-
# th_regione.py

from gnr.web.gnrbaseclasses import BaseComponent


class Form(BaseComponent):
    def th_form(self,form):
        bc = form.center.borderContainer()
        fb = bc.contentPane(region='top',datapath='.record').formbuilder(cols=1, margin_left='2em',border_spacing='7px',margin_top='1em')
        fb.field('nome', width='20em')
        fb.field('sigla',width='3em')
        fb.field('codice_istat',width='7em')
        fb.field('zona')
        bc.contentPane(region='center').inlineTableHandler(relation='@province',region='center',
                                                          viewResource='ViewFromRegione',pbl_classes=True,margin='2px')
                                                                
class View(BaseComponent):
    def th_struct(self,struct):
        r = struct.view().rows()
        r.fieldcell('nome', width='20em')
        r.fieldcell('sigla',width='3em')
        r.fieldcell('codice_istat',width='7em',sortable=False)
        r.fieldcell('zona',width='100%')

    

    def th_order(self):
        return 'nome'

    def th_query(self):
        return dict(column='nome',op='contains', val='')
