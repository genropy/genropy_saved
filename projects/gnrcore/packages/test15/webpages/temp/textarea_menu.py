# -*- coding: UTF-8 -*-

# textarea_menu.py
# Created by Francesco Porcari on 2012-04-13.
# Copyright (c) 2012 Softwell. All rights reserved.

"Test page description"
class GnrCustomWebPage(object):
    py_requires="gnrcomponents/testhandler:TestHandlerFull"

    def windowTitle(self):
        return ''
 
    def test_0_firsttest(self,pane):
        """First test description"""
        m = pane.simpleTextArea(value='^.piero').menu(action="""
            console.log(this,$1,$2,$3);
            var fn = $2.widget.focusNode;
            var ss = fn.selectionStart;
            var se = fn.selectionEnd;
            var v =  fn.value;
            var fistchunk = v.slice(0,ss);
            var secondchunk = v.slice(se);
            fn.value = fistchunk+$1.caption+secondchunk;
            """)
        m.menuline('pippo',caption='Pippo')
        m.menuline('paperino',caption='Paperino')
        pane.simpleTextArea(value='^.mario')
    
    def test_1_base(self, pane):
        """Basic 2"""
        menudiv = pane.div(height='20px',width='50px',background='teal')
        menu = menudiv.menu(action='alert($1.foo)')
        menu.menuline('abc',foo=35)
        menu.menuline('xyz',foo=60,disabled=True)
        menu.menuline('alpha',action='alert("I\'m different")',checked=True)
        menu.menuline('-')
        submenu = menu.menuline('Sub').menu(action='alert("sub "+$1.bar)')
        submenu.menuline('cat',bar=35)
        submenu.menuline('dog',bar=60)
        