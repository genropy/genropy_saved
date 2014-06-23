
# # -*- coding: UTF-8 -*-

# menuselect.py
# Created by Francesco Porcari on 2011-08-29.
# Copyright (c) 2011 Softwell. All rights reserved.

"Test page description"
from gnr.core.gnrbag import Bag
class GnrCustomWebPage(object):
    py_requires="gnrcomponents/testhandler:TestHandlerFull"

    def windowTitle(self):
        return ''
         
    def test_0_firsttest(self,pane):
        """First test description"""
        b = Bag()
        b.setItem('foo',None,caption='Test 1')
        b.setItem('foo.bar',None,caption='Test 2',color='red')
        b.setItem('spam',None,caption='Test 3')

        pane.data('.menu',b)
        pane.div('^.value?caption',min_width='40px',min_height='16px',display='inline-block',padding_left='4px',
                border='1px solid silver',background='white',rounded=4).menu(storepath='.menu',
                             selected_fullpath='.value',
                             modifiers='*')
        pane.dataController("""
                            if($2.kw.updvalue){
                                var path = this.absDatapath('.value');
                                genro._data.setAttr(path,b.getNode(p).attr);
                            }
                            """,p="^.value",b='=.menu')