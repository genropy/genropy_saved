# -*- coding: utf-8 -*-

# th_localita.py
# Created by Francesco Porcari on 2011-03-31.
# Copyright (c) 2011 Softwell. All rights reserved.
from gnr.web.gnrbaseclasses import BaseComponent
from gnr.core.gnrdecorator import customizable,metadata,public_method

class Form(BaseComponent):

    def th_form(self,form,**kwargs):
        pane = form.record
        fb = pane.formbuilder(cols=1, margin_left='2em',border_spacing='5px')
        fb.field('nome', width='20em')
        fb.field('sigla',width='3em')
        fb.field('codice_istat',width='7em')
        fb.field('regione')
        
    def th_options(self):
        return dict(dialog_height='180px',dialog_width='400px')

class View(BaseComponent):
    def th_struct(self,struct):
        r = struct.view().rows()
        r.fieldcell('nome', width='20em')
        r.fieldcell('sigla',width='3em')
        r.fieldcell('codice_istat',width='7em')
        r.fieldcell('regione',width='100%')

    def th_order(self):
        return 'nome'

    def th_query(self):
        return dict(column='nome',op='contains', val='')

   #def th_sections_zone(self):
   #    return [dict(code='nord',caption='!![it]Nord',condition='@regione.zona ILIKE :zona',condition_zona='%%Nord%%'),
   #            dict(code='centro',caption='!![it]Centro',condition='@regione.zona=:zona',condition_zona='Centro'),
   #            dict(code='sud',caption='!![it]Sud',condition='@regione.zona=:zona',condition_zona='Sud'),
   #            dict(code='isole',caption='!![it]Isole',condition='@regione.zona=:zona',condition_zona='Isole')]
                
    @public_method(remote_zona='^.zone.current')
    def sectionRegioni(self,zona=None):
        f = self.db.table('glbl.regione').query(where='$zona ILIKE :zona',zona=zona).fetch()
        return [dict(code='reg_%(sigla)s' %r, caption=r['nome'],condition='$regione=:rg',condition_rg=r['sigla']) for r in f]

    def th_top_custom(self,top):
        top.bar.replaceSlots('searchOn','searchOn,sections@zone,sections@reg',sections_reg_remote=self.sectionRegioni)


    def th_options(self):
        return dict(virtualStore=False)



class ViewFromRegione(BaseComponent):    
    def th_struct(self,struct):
        r = struct.view().rows()
        r.fieldcell('sigla',width='3em',edit=True)
        r.fieldcell('nome', width='20em',edit=True,name='Nome')
        r.fieldcell('codice_istat',width='7em',sortable=False,edit=True)
        
    def th_order(self):
        return 'nome'


        

