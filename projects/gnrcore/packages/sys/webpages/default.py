# -*- coding: UTF-8 -*-

# untitled.py
# Created by Giovanni Porcari on 2010-08-29.
# Copyright (c) 2010 Softwell. All rights reserved.

from gnr.core.gnrbag import Bag,DirectoryResolver
import re
import os
class GnrCustomWebPage(object):
    css_requires='public'

    def pageAuthTags(self, method=None, **kwargs):
        return ''

    def windowTitle(self):
        return ''
    def isDeveloper(self):
        return True

    def main(self, root, **kwargs):
        call_args = self.getCallArgs()
        info = self.site.resource_loader.getUrlInfo(call_args)
        root.data('pages_tree',self._get_dir_tree(os.path.join(info.basepath,*info.request_args)))
        bc=root.borderContainer()
        left=bc.contentPane(region='left',width='200px',splitter=True,background='#eee',overflow_y='auto')
        center=bc.contentPane(region='center')
        left.dataController( """
            var n = treestore.getNode('root.'+x,'static');
            if (n._value){
                SET current_url = '';
            }
            SET current_url = x;
       """,  #"current_url","x?('/'+prefix+'/'+x).replace(/\/\//g,'/'):'' ",
            x='^tree.rel_path',treestore='=pages_tree')
        left.tree(storepath='pages_tree.root', hideValues=True, 
                inspect='shift', labelAttribute='caption',
              getIconClass='return node.attr.iconClass || "treeNoIcon"',
              getLabelClass="""var _class= (node._resolver || node._value) ? 'menu_shape menu_level_0' :  'menu_shape menu_level_2';
                               console.log(node,_class);return _class""",
              isTree=False, selected_rel_path='tree.rel_path',  _class='menutree',
              openOnClick=True,
              autoCollapse=True,
              connect_ondblclick='genro.openWindow(GET current_url);',
              selected_name='tree.name')
        center.iframe(border='0px',width='100%',height='100%',src='^current_url')
        return


    def _get_dir_tree(self,basepath=None):
        result = Bag()
        result.setItem('root', DirectoryResolver(basepath,cacheTime=10,
                            include='*.py', exclude='_*,.*',dropext=True,readOnly=False
                            #callback=self.getCaption
                            ))
        return result

    def getCaption(self,nodeattr):
        file_name = nodeattr['file_name']
        m=re.match(r'(\d+)_(.*)',file_name)
        name = '!!%s_%s' % (str(int(m.group(1))),m.group(2).capitalize()) if m else file_name.capitalize()
        return name



