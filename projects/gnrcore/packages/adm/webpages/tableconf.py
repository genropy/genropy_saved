# -*- coding: UTF-8 -*-

# thpage.py
# Created by Francesco Porcari on 2011-05-05.
# Copyright (c) 2011 Softwell. All rights reserved.

from gnr.core.gnrbag import Bag
from gnr.core.gnrdecorator import public_method

class GnrCustomWebPage(object):
    py_requires='public:Public,th/th:TableHandler'
    css_requires = 'public'
    
    @classmethod
    def getMainPackage(cls,request_args=None,request_kwargs=None):
        return request_kwargs.get('th_from_package') or request_args[0]
        
   # @property
   # def maintable(self):
   #     callArgs = self.getCallArgs('conf_pkg','conf_table','branch')
   #     return '%(conf_pkg)s.%(conf_table)s' %callArgs
#
    @property
    def pagename(self):
        callArgs = self.getCallArgs('conf_pkg','conf_table','branch') 
        callArgs['branch']  = callArgs['branch'] or 'main'
        return 'tableconf_%(conf_pkg)s_%(conf_table)s_%(branch)s' %callArgs

    def main(self,root,th_pkey=None,**kwargs):
        callArgs = self.getCallArgs('conf_pkg','conf_table','branch') 
        tpl = '%(conf_pkg)s.%(conf_table)s/%(branch)s' if callArgs.get('branch') else '%(conf_pkg)s.%(conf_table)s'
        root.thFormHandler(table='adm.tblinfo',formResource='FormFromTH',datapath='main',
                        startKey=tpl %callArgs)




