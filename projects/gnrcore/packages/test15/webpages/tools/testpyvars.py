# -*- coding: UTF-8 -*-
# 
"""ClientPage tester"""

class GnrCustomWebPage(object):
    py_requires = "gnrcomponents/testhandler:TestHandlerFull,"

    def test_1_a(self, pane):
        """Set in external store"""
        fb=pane.formbuilder(cols=1)
        tb1 = fb.textbox(value='^aaa',lbl='aaa',)
        fb.textbox(value='^bbb',lbl='bbb')
        fb.div('^ccc')
        pane.dataFormula('ccc','a+" - "+b',a='^aaa',b='^bbb')
        btn = pane.button(label='ffff',action="console.log(tb1.widget)",tb1=tb1)
                
    def test_2_b(self, pane):
        xxx = pane.button(label='ttt')
        box = pane.div(height='12px',width='12px',background='red',
                        selfsubscribe_test='console.log(btn)',
                        btn=xxx,
                        connect_onclick='console.log(this.inheritedAttribute("btn"));'
                        )
        
        pane.button('test 2',action='box.publish("test")',box=box)

    def test_3_c(self,pane):
        box = pane.div(height='20px',width='500px',
                     selfsubscribe_dimmi_larghezza='this.domNode.innerHTML=this.attr.width;',background='white')
        box2 = pane.div(height='20px',width='300px',
                     selfsubscribe_dimmi_larghezza='this.domNode.innerHTML= this.attr.width;',background='green')
        pane.button('Dimmi A',action='box.publish("dimmi_larghezza");',box=box)
        pane.button('Dimmi B',action='box.publish("dimmi_larghezza");',box=box2)