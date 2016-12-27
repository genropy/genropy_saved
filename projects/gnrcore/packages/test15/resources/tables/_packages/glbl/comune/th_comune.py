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
                name=u'Sì',totalize='#FORM.record.mill_si',format='#,###,###')

        r.cell('n_voti_no',calculated=True,width='7em',
            columnset='po',totalize='#FORM.record.mill_no',
                formula='voto_no?popolazione_residente:0',dtype='L',name='No',format='#,###,###')
        r.cell('n_voti_astenuto',calculated=True,width='7em',
            columnset='po',totalize='#FORM.record.mill_ast',
                formula='voto_astenuto?popolazione_residente:0',
                    dtype='L',name='Astenuti',format='#,###,###')
        r.cell('n_voti_assenti',calculated=True,width='7em',
            columnset='po',
                formula='!(voto_astenuto||voto_si||voto_no)?popolazione_residente:0',
                    dtype='L',name='Assenti',totalize=True,format='#,###,###')
        r.fieldcell('popolazione_residente', width='7em',
            columnset='po',
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


    def th_options(self):
        return dict(grid_columnset_voto='Votazione',grid_columnset_po='Popolazione',
                    grid_footer='Totali Voto')
