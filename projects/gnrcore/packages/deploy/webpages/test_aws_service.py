# -*- coding: UTF-8 -*-

# test_aws_service.py
# Created by Francesco Porcari on 2011-01-10.
# Copyright (c) 2011 Softwell. All rights reserved.

"""test aws_service"""
from gnr.core.gnrbag import Bag
from gnr.core.gnrdecorator import public_method

class GnrCustomWebPage(object):
    py_requires="gnrcomponents/testhandler:TestHandlerFull"
    css_requires='public'
    
    def windowTitle(self):
        return 'Test AWS Manager'
         
    def test_0_getInstances(self,pane):
        pane.button('Get instances', action='FIRE .getInstances;')
        pane.dataRpc('.instances_data', self.getInstancesData, _fired='^.getInstances')
        pane.quickGrid(value='^.instances_data', height='500px')

    @public_method
    def getInstancesData(self):
        aws_manager = self.site.getService('aws_softwell')
        return aws_manager.ec2_instances()
        