# -*- coding: UTF-8 -*-
# 
"""ClientPage tester"""

class GnrCustomWebPage(object):
    py_requires = "gnrcomponents/testhandler:TestHandlerFull,"

    def test_1_(self, pane):
        """Set in external store"""
        fb=pane.formbuilder(cols=1)
        tb1=fb.textbox(value='^aaa',lbl='aaa',)
        fb.textbox(value='^bbb',lbl='bbb')
        fb.div('^ccc')
        pane.dataFormula('ccc','a+" - "+b',a='^aaa',b='^bbb')
        pane.button(label='ffff',action="console.log(tb1)",tb1=tb1)


