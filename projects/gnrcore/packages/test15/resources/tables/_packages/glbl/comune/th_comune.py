# -*- coding: utf-8 -*-

# th_localita.py
# Created by Francesco Porcari on 2011-03-31.
# Copyright (c) 2011 Softwell. All rights reserved.
from gnr.web.gnrbaseclasses import BaseComponent
from gnr.core.gnrdecorator import metadata,public_method

class TestComunePiuBello(BaseComponent):
    def th_struct(self,struct):
        r = struct.view().rows()
        r.fieldcell('denominazione', width='20em',edit=True
            )
        r.checkboxcolumn(radioButton=True,checkedId='#FORM.comunePiuBello')


class TestViewVotoRadio(BaseComponent):
    def th_struct(self,struct):
        r = struct.view().rows()
        r.checkboxcolumn('capoluogo',name='C',radioButton=True)
        r.fieldcell('denominazione', width='20em',edit=True)

        voto = r.columnset('voto',name='Votazione')
        voto.checkboxcolumn('voto_si',radioButton='voto',
                        name=u'Sì',width='4em')
        voto.checkboxcolumn('voto_no',radioButton='voto',
                        name='No',width='4em')
        voto.checkboxcolumn('voto_astenuto',radioButton='voto',
                        name='Ast.',width='4em')

        meteo = r.columnset('meteo',name='Meteo',background='darkgreen')
        meteo.checkboxcolumn('brutto',radioButton='mt',
                        name=u'Brutto',width='4em')
        meteo.checkboxcolumn('bello',radioButton='mt',
                        name='Bello',width='4em')
        meteo.checkboxcolumn('medio',radioButton='mt',
                        name='Medio',width='4em')

        pop = r.columnset('pop',name='Popolazione')

        pop.cell('n_voti_si',calculated=True,width='7em',
                formula='voto_si?popolazione_residente:0',dtype='L',
                name=u'Sì',totalize='#FORM.record.mill_si',format='#,###,###')

        pop.cell('n_voti_no',calculated=True,width='7em',
            totalize='#FORM.record.mill_no',
                formula='voto_no? popolazione_residente:0',
                dtype='L',name='No',format='#,###,###')
        pop.cell('n_voti_astenuto',calculated=True,width='7em',
            totalize='#FORM.record.mill_ast',
                formula='voto_astenuto?popolazione_residente:0',
                    dtype='L',name='Astenuti',format='#,###,###')
        pop.cell('n_voti_assenti',calculated=True,width='7em',
                formula='!(voto_astenuto||voto_si||voto_no)?popolazione_residente:0',
                    dtype='L',name='Assenti',totalize=True,format='#,###,###')
        pop.fieldcell('popolazione_residente', width='7em',
            name='Totale',totalize=True,format='#,###,###')

    def th_order(self):
        return 'denominazione'


    def th_view(self,view):
        grid = view.grid
        f = grid.footer(background_color='#B0CCEB')
        f.item('denominazione',value='Percentuali',colspan=4,text_align='right')
        f.item('n_voti_si',value='^.perc.voti_si',text_align='right',format='##.00')
        f.item('n_voti_no',value='^.perc.voti_no',text_align='right',format='##.00')
        f.item('n_voti_astenuto',value='^.perc.voti_astenuti',text_align='right',format='##.00')
        f.item('n_voti_assenti',value='^.perc.voti_assenti',text_align='right',format='##.00')
        f.item('popolazione_residente',value='100.00',text_align='right')
        view.grid.dataController("""
            var si = Math.round10(n_voti_si*100/n_voti_totali,-2);
            var no =  Math.round10(n_voti_no*100/n_voti_totali,-2);
            var ast = Math.round10(n_voti_astenuti*100/n_voti_totali,-2);
            SET .perc.voti_si = si;
            SET .perc.voti_no = no;
            SET .perc.voti_astenuti = ast;
            SET .perc.voti_assenti = 100-si-no-ast;
            """,n_voti_si='^#FORM.record.mill_si',
                n_voti_no='^#FORM.record.mill_no',
                n_voti_astenuti='^#FORM.record.mill_ast',
                n_voti_totali='^.totalize.popolazione_residente',_delay=1)

        view.top.bar.replaceSlots('vtitle','vtitle,filterset@per_voto')

    def th_filterset_per_voto(self):
        return [dict(code='tutti',caption='Tutti'),
                dict(code='voto_si',caption=u'Sì',cb='voto_si'),
                dict(code='voto_no',caption=u'No',cb='voto_no',isDefault=True),
                dict(code='voto_ast',caption=u'Astenuti',cb='voto_astenuto'),
                dict(code='voto_ass',caption=u'Assenti',cb='!(voto_si || voto_no || voto_astenuto)')
                ]


    def th_options(self):
        return dict(grid_footer='Totali Voto')
