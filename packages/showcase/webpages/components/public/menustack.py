#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-

#  Created by Giovanni Porcari on 2007-03-24.
#  Copyright (c) 2007 Softwell. All rights reserved.

class GnrCustomWebPage(object):
    py_requires='public:Public,foundation/macrowidgets:MenuStackContainer'
    def main(self, rootBC, **kwargs):
        sc = self.menuStackContainer(rootBC,nodeId='foo',region='center',fixed=True,
                                    selectedPage='^bar',**kwargs)
        sc.borderContainer(title='John',background='green',pageName='john')
        sc.tabContainer(title='Smith',background='red',pageName='smith')
        sc.borderContainer(title='Jeff',background='blu',pageName='jeff')
        sc.borderContainer(title='Edw',background='purple',pageName='edw')