# -*- coding: UTF-8 -*-
# th_regione.py

from gnr.web.gnrbaseclasses import BaseComponent
from gnr.core.gnrdecorator import public_method

class Form(BaseComponent):

    def th_form(self,form,**kwargs):
        
        pane = form.record
        fb = pane.formbuilder(cols=1, margin_left='2em',border_spacing='7px',margin_top='1em')
        fb.field('nome', width='20em')
        fb.field('sigla',width='3em')
        fb.field('codice_istat',width='7em')
        fb.field('zona')
        
    def th_dialog(self):
        return dict(height='300px',width='500px')



class FormBug(BaseComponent):
    def th_form(self,form,**kwargs):
        bc = form.center.borderContainer()
        fb = bc.contentPane(region='top',datapath='.record').formbuilder(cols=1, margin_left='2em',border_spacing='7px',margin_top='1em')
        fb.field('nome', width='20em')
        fb.field('sigla',width='3em')
        fb.field('codice_istat',width='7em')
        fb.field('zona')
        th = bc.contentPane(region='center').borderTableHandler(relation='@province')
        th.view.attributes.update(region='left',width='400px',height=None)

class FormConProvince(BaseComponent):
    def th_form(self,form):
        bc = form.center.borderContainer()
        fb = bc.contentPane(region='top',datapath='.record').formbuilder(cols=1, margin_left='2em',border_spacing='7px',margin_top='1em')
        fb.field('nome', width='20em')
        fb.field('sigla',width='3em')
        fb.field('codice_istat',width='7em')
        fb.field('zona')
        th = bc.contentPane(region='center').inlineTableHandler(relation='@province',region='center',
                                                                viewResource=':EditableView',statusColumn=True)
        bar = th.view.top.bar
        bar.replaceSlots('addrow','addrow,savegrid')
        bar.savegrid.slotButton('Save',action='grid.widget.gridEditor.saveChangedRows();',grid=th.view.grid)
        #th = bc.contentPane(region='center').dialogTableHandler(relation='@province',dialog_height='300px',
        #                                                        dialog_width='500px',default_)
    
    
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
