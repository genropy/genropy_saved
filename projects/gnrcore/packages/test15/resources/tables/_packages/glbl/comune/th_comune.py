# -*- coding: UTF-8 -*-

# th_localita.py
# Created by Francesco Porcari on 2011-03-31.
# Copyright (c) 2011 Softwell. All rights reserved.
from gnr.web.gnrbaseclasses import BaseComponent
from gnr.core.gnrdecorator import metadata,public_method


class TestViewVotoRadio(BaseComponent):
    def th_struct(self,struct):
        r = struct.view().rows()
        r.fieldcell('denominazione', width='20em',edit=True
            )
 
        r.checkboxcolumn('voto_si',radioButton='voto',
            columnset='voto',name=u'Sì',width='4em')
        r.checkboxcolumn('voto_no',radioButton='voto',
            columnset='voto',name='No',width='4em')
        r.checkboxcolumn('voto_astenuto',radioButton='voto',
            columnset='voto',name='Ast.',width='4em')
       
        r.cell('n_voti_si',calculated=True,width='7em',
                formula='voto_si?popolazione_residente:0',dtype='L',
                columnset='po',
                name=u'Sì',totalize=True)

        r.cell('n_voti_no',calculated=True,width='7em',
            columnset='po',
                formula='voto_no?popolazione_residente:0',dtype='L',name='No',totalize=True)
        r.cell('n_voti_astenuto',calculated=True,width='7em',
            columnset='po',
                formula='voto_astenuto?popolazione_residente:0',
                    dtype='L',name='Astenuti',totalize=True)
        r.fieldcell('popolazione_residente', width='7em',edit=True,
            columnset='po',
            name='Totale',totalize=True)
        
    def th_order(self):
        return 'denominazione'

    def th_options(self):
        return dict(grid_columnset_voto='Votazione',grid_columnset_po='Popolazione',
                    grid_footer='Totali Voto')
