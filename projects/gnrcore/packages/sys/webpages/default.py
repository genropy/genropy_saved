# -*- coding: UTF-8 -*-

# untitled.py
# Created by Giovanni Porcari on 2010-08-29.
# Copyright (c) 2010 Softwell. All rights reserved.

class GnrCustomWebPage(object):
    css_requires='public'

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
            left=bc.contentPane(region='left',width='200px',splitter=True,background='#eee',overflow_y='auto')
            center=bc.contentPane(region='center')
            prefix=''.join(self.getCallArgs())
            left.dataFormula("current_url","'/'+prefix+'/'+x",x='^tree.current_path',prefix=prefix)
            left.tree(storepath='pages_tree', hideValues=True, inspect='shift', labelAttribute='name',
                  getIconClass='return node.attr.iconClass || "treeNoIcon"',
                  getLabelClass="""var _class= (node._resolver || node._value) ? 'menu_shape menu_level_0' :  'menu_shape menu_level_2';
                                   console.log(node,_class);return _class""",
                  isTree=False, selected_path='tree.current_path',  _class='menutree',
                  openOnClick=True,
                  autoCollapse=True,
                  connect_ondblclick='genro.openWindow(GET current_url);',
                  selected_name='tree.name')
            center.iframe(border='0px',width='100%',height='100%',src='^current_url')
            
        return