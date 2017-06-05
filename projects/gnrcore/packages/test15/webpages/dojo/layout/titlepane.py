# -*- coding: UTF-8 -*-

# tab.py
# Created by Francesco Porcari on 2010-12-20.
# Copyright (c) 2010 Softwell. All rights reserved.

"""tabContainer"""

class GnrCustomWebPage(object):
    py_requires = "gnrcomponents/testhandler:TestHandlerFull"
    css_requires = 'test'
    dojo_source=True
    
    def windowTitle(self):
        return ''
        
    def test_0_table(self, pane):
        tbl = pane.table(width='500px')
        h = tbl.thead()
        h.th()
        h.th('2016',width='10em',text_align='center')
        h.th('2015',width='10em',text_align='center')
        h.th('',width='2em')
        tb = tbl.tbody()
        r = tb.tr()
        r.td('Attivo')
        r.td('50.500',text_align='right')
        r.td('80.200',text_align='right')
        r.td().lightbutton(_class='iconbox tinyOpenBranch')
        r = tb.tr()
        r.td('Credito verso soci',text_indent='20px')
        r.td('30.500',text_align='right')
        r.td('0',text_align='right')
        r.td().lightbutton(_class='iconbox tinyOpenBranch')

        r = tb.tr()
        r.td('Mario rossi',text_indent='50px')
        r.td('10.500',text_align='right')
        r.td('0',text_align='right')

        r = tb.tr()
        r.td('Luigi bianchi',text_indent='50px')
        r.td('20.000',text_align='right')
        r.td('0',text_align='right')

        r = tb.tr()
        r.td('Credito verso banche',text_indent='20px')
        r.td('10.000',text_align='right')
        r.td('0',text_align='right')
        r.td().lightbutton(_class='iconbox tinyOpenBranch')

        r = tb.tr()
        r.td('Creval',text_indent='50px')
        r.td('5.500',text_align='right')
        r.td('0',text_align='right')

        r = tb.tr()
        r.td('Banco Popolare',text_indent='50px')
        r.td('4.500',text_align='right')
        r.td('0',text_align='right')


    def test_1_table(self, pane):
        #pane.css('.ittc-Attivo_chiuso .ittc-Attivo','display:none')
        #pane.css('.ittc-Soci_chiuso .ittc-Soci','display:none')
        #pane.css('.ittc-Banche_chiuso .ittc-Banche','display:none')

        tbl = pane.table(width='500px',_class='ittc-Soci_chiuso')
        pane.style("""
            .ittc-Attivo_chiuso .ittc-Attivo{
                display:none;
            }
            .ittc-Soci_chiuso .ittc-Soci{
                display:none;
            }
            .ittc-Banche_chiuso .ittc-Banche{
                display:none;
            }
            """)
        h = tbl.thead()
        h.th()
        h.th('2016',width='10em',text_align='center')
        h.th('2015',width='10em',text_align='center')
        h.th('',width='2em')
        tb = tbl.tbody()
        r = tb.tr()
        r.td('Attivo')
        r.td('50.500',text_align='right')
        r.td('80.200',text_align='right')
        r.td().lightbutton(_class='iconbox tinyOpenBranch')
        r = tb.tr(_class='ittc-Attivo')
        r.td('Credito verso soci',text_indent='20px')
        r.td('30.500',text_align='right')
        r.td('0',text_align='right')
        r.td().lightbutton(_class='iconbox tinyOpenBranch')

        r = tb.tr(_class='ittc-Attivo ittc-Soci')
        r.td('Mario rossi',text_indent='50px')
        r.td('10.500',text_align='right')
        r.td('0',text_align='right')

        r = tb.tr(_class='ittc-Attivo ittc-Soci')
        r.td('Luigi bianchi',text_indent='50px')
        r.td('20.000',text_align='right')
        r.td('0',text_align='right')

        r = tb.tr(_class='ittc-Attivo')
        r.td('Credito verso banche',text_indent='20px')
        r.td('10.000',text_align='right')
        r.td('0',text_align='right')
        r.td().lightbutton(_class='iconbox tinyOpenBranch')

        r = tb.tr(_class='ittc-Attivo itcc-Banche')
        r.td('Creval',text_indent='50px')
        r.td('5.500',text_align='right')
        r.td('0',text_align='right')

        r = tb.tr(_class='ittc-Attivo itcc-Banche')
        r.td('Banco Popolare',text_indent='50px')
        r.td('4.500',text_align='right')
        r.td('0',text_align='right')
