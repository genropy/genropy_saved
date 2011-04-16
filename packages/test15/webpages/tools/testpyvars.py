# -*- coding: UTF-8 -*-
# 
"""ClientPage tester"""

class GnrCustomWebPage(object):
    py_requires = "gnrcomponents/testhandler:TestHandlerFull,"

    def test_1_a(self, pane):
        """Set in external store"""
        fb=pane.formbuilder(cols=1)
        tb1=fb.textbox(value='^aaa',lbl='aaa',)
        fb.textbox(value='^bbb',lbl='bbb')
        fb.div('^ccc')
        pane.dataFormula('ccc','a+" - "+b',a='^aaa',b='^bbb')
        
        btn = pane.button(label='ffff',action="console.log(tb1)",tb1=tb1)

    def test_2_b(self, pane):
        xxx = pane.button(label='ttt')
        box = pane.div(height='12px',width='12px',background='red',
                        selfsubscribe_test='genro.bp();console.log(btn)',
                        btn=xxx,
                        connect_onclick='console.log(btn);'
                        )
        
        pane.button('test 2',action='box.publish("test")',box=box)

