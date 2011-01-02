#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-

#  Created by Giovanni Porcari on 2007-03-24.
#  Copyright (c) 2007 Softwell. All rights reserved.

class GnrCustomWebPage(object):
    py_requires = 'public:Public,foundation/dialogs'

    def main(self, rootBC, **kwargs):
        pane = rootBC.contentPane(margin='5px')
        pane.button('open 1', action='SET framepage_test ="/showcase/catalog/component/res/test1"; FIRE #myframe.open;')
        pane.button('open 2', action='SET framepage_test ="/showcase/catalog/component/res/test2"; FIRE #myframe.open;')

        self.iframeDialog(pane, title='test iframe', dlgId='myframe', height='300px',
                          width='400px', src='=framepage_test', datapath='test')