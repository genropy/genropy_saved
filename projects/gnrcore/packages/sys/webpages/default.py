# -*- coding: UTF-8 -*-

# untitled.py
# Created by Giovanni Porcari on 2010-08-29.
# Copyright (c) 2010 Softwell. All rights reserved.

class GnrCustomWebPage(object):
    #py_requires='public:Public'

    def pageAuthTags(self, method=None, **kwargs):
        return ''

    def windowTitle(self):
        return ''
    def isDeveloper(self):
        return True
    def main(self, root, **kwargs):
        node=self.site.sitemap.getDeepestNode('.'.join(self.getCallArgs()))
        if not node:
            root.h1('Not existing page')
        else:
            root.data('pages_tree',node.value)
            bc=root.borderContainer()
            top=bc.contentPane(region='top',height='120px')
            top.div('^tree.current_path')
            center=bc.contentPane(region='center')
            prefix=''.join(self.getCallArgs())
            center.dataController("""
                                    genro.gotoURL(prefix+'/'+x);
                                """,x='^tree.current_path',prefix=prefix)
            center.tree(storepath='pages_tree', hideValues=True, inspect='shift', labelAttribute='name',
                  isTree=False, selected_path='tree.current_path',  _class='menutree',
                  selected_name='tree.name')
            
        return