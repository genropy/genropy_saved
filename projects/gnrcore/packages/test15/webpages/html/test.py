# -*- coding: UTF-8 -*-

"""Html elements tester"""

class GnrCustomWebPage(object):
    py_requires = "gnrcomponents/testhandler:TestHandlerBase"
    dojo_theme = 'claro'
    
    def test_1_basic(self, pane):
        """Basic test for a div with no attributes"""
        pane.div('Basic div no attributes')
        
    def test_2_div_with_styles(self, pane):
        """Div with styles"""
        pane.div('Styled div', height='50px', width='100px', border='2px dotted red', background_color='yellow')
        
    def test_3_some_span(self, pane):
        """Some spans"""
        pane.span('this is: ')
        pane.span('green ', color='green')
        pane.span('yellow ', color='yellow')
        pane.span('red', color='red')
        
    def test_4_htmltable(self, pane):
        """Html table"""
        t = pane.table()
        tbody = t.tbody()
        for k in range(6):
            row = tbody.tr()
            for j in range(6):
                row.td('cell: %i' % ((k + 1) * 6 + j), border='1px solid green')
                