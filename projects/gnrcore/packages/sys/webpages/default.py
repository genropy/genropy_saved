# -*- coding: utf-8 -*-

# untitled.py
# Created by Giovanni Porcari on 2010-08-29.
# Copyright (c) 2010 Softwell. All rights reserved.

from builtins import object
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
        url_info = self.site.getUrlInfo(self.getCallArgs())
        dirpath=os.path.join(url_info.basepath,*url_info.request_args)
        bc=root.borderContainer(datapath='main')
        bc.style(""".menutree .opendir{
                width: 12px;
                background: url(/_gnr/11/css/icons/base10/tinyOpenBranch.png) no-repeat center center;
            }
            .menutree .closedir{
                width: 12px;
                background: url(/_gnr/11/css/icons/base10/tinyCloseBranch.png) no-repeat center center;
            }
        """)
        center=bc.contentPane(region='center',datapath='.current')
        left=bc.contentPane(region='left',width='200px',splitter=True,background='#eee',
                           datapath='.tree',overflow_y='auto')
        left.data('.store',DirectoryResolver(dirpath,cacheTime=10,
                            include='*.py', exclude='_*,.*',dropext=True,readOnly=False)()
                            )
        center.dataFormula(".url","(window.location.pathname+'/'+rel_path).replace('//','/')",
                                  _if="file_ext=='py'",_else="''",
                                   rel_path='^.rel_path',file_ext='=.file_ext')                   
        left.tree(storepath='.store', hideValues=True, inspect='shift', 
              labelAttribute='caption',
               getIconClass="""
               function(item,opened){
                        console.log('item.attr',item.attr);
                        if(item.attr.file_ext!='directory'){
                            return "treeNoIcon";
                        }
                        return opened? 'opendir':'closedir';                        
                    }""",
              getLabelClass="""var _class= (node._resolver || node._value) ? 'menu_shape menu_level_0' :  'menu_shape menu_level_2';
                                            return _class""",
              isTree=False, selected_rel_path='main.current.rel_path',  _class='menutree',
              openOnClick=True,
              autoCollapse=True,
              connect_ondblclick='window.open(GET main.current.url,GET main.current.caption);',
              selected_caption='main.current.caption',
              selected_file_ext='main.current.file_ext')
        center.iframe(border='0px',width='100%',height='100%',src='^.url')


