# -*- coding: utf-8 -*-
            
from gnr.core.gnrdecorator import public_method
from gnr.app.gnrdeploy import projectBag
from gnr.core.gnrbag import Bag
 

class GnrCustomWebPage(object):
    py_requires='gnrcomponents/externalcall:NetBagRpc'

    @public_method(tags='ext,_DEV_')
    def netbag_infoproject(self,project=None,packages=None,branches=None,**kwargs):
        prjbag = projectBag(project,packages=packages,branches=branches)
        return prjbag