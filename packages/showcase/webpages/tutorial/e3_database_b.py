#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-

class GnrCustomWebPage(object):
    py_requires = 'demo:Demo'

    def main(self, root, **kwargs):
        root.dataFormula('font_size', 'Math.ceil(font)+umf', font='^font', umf='^um_font')
        root.dataFormula('width_calc', 'Math.ceil(w)+umw', w='^width', umw='^um_width')
        bc = root.borderContainer(height='100%')
        top = bc.contentPane(height='400px', region='top')
        top.dbSelect(value='^anagrafica.id', dbtable='assopy.anagrafica',
                     margin='10px', columns='ragione_sociale', font_size='^font_size',
                     width='^width_calc',
                     auxColumns='localita,provincia,cap,codice_fiscale,partita_iva')
        center = bc.contentPane(region='center')

        fb = center.formbuilder(cols=3, margin_top='10px')
        fb.br()
        fb.horizontalslider(lbl='!!width', value='^width', width='200px',
                            minimum=3, maximum=50, intermediateChanges=True)
        fb.numberTextBox(value='^width', width='5em')
        fb.comboBox(width='5em', values='em,px,%', value='^um_width', default='em')
        fb.horizontalslider(lbl='!!font', value='^font', width='200px',
                            minimum=4, maximum=50, intermediateChanges=True)
        fb.numberTextBox(value='^font', width='5em')

        fb.comboBox(width='5em', values='pt,px', value='^um_font', default='pt')