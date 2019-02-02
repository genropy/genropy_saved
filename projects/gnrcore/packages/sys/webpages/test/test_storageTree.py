# -*- coding: utf-8 -*-
#
#  Created by Francesco Porcari 
#  Copyright (c) 2018 Softwell. All rights reserved.
#

from builtins import object
from gnr.core.gnrdecorator import public_method
from gnr.core.gnrbag import Bag

class GnrCustomWebPage(object):
    py_requires="gnrcomponents/testhandler:TestHandlerFull,gnrcomponents/storagetree:StorageTree"

    def pageAuthTags(self, **kwargs):
        return 'user'

    def windowTitle(self):
        return '!!Test storagetree'

    def test_01_storageTree(self, pane, **kwargs):
        pane.dbselect(value='^.service_id', table='sys.services', where='$service_type = :st', st='storage', hasDownArrow=True,
            selected_service_name='.servicename')
        pane.textbox(value='^.storagepath',width='60em')
        pane.storageTreeFrame(frameCode='ftelBucket',storagepath='^.storagepath',border='1px solid silver',
                                store__onStart=True,height='400px',preview_region='right',
                                preview_border_left='1px solid silver',preview_width='50%')

    def test_02_storageNode(self, pane, **kwargs):
        pane.textbox(value='^.storagepath',width='60em')
        box = pane.div(_class='selectable')
        box.dataRpc('.result',self.testStorageNode,storagepath='^.storagepath')
        box.div('^.result?=#v?#v.getFormattedValue():""')

    @public_method
    def testStorageNode(self,storagepath=None):
        n = self.site.storageNode(storagepath)
        result = Bag()
        if not n.exists:
            result['error'] = 'Not existing path'
        else:
            result['path'] = n.path
            result['url'] = n.url()
            result['isdir'] = n.isdir
            result['service_name'] = n.service.service_name
            result['service_implementation'] = n.service.service_implementation
            result['size'] = n.size
        return result
        
