#!/usr/bin/env pythonw
# -*- coding: utf-8 -*-
#
#  Created by Saverio Porcari on 2013-04-06.
#  Copyright (c) 2013 Softwell. All rights reserved.


from gnr.lib.services import GnrBaseService
from subprocess import call
import os


class Main(GnrBaseService):
    def __init__(self, parent=None):
        self.parent = parent

    def convert(self,src_path, dest_path=None):
        sourceStorageNode = self.parent.storageNode(src_path)
        if not dest_path:
            dirname = sourceStorageNode.dirname
            basename = sourceStorageNode.basename
            destStorageNode = self.parent.storageNode(dirname,'converted_pdf','%s.pdf' %sourceStorageNode.cleanbasename)
        else:
            destStorageNode =  self.parent.storageNode(dest_path)
        destname = destStorageNode.cleanbasename
        counter = 0

        while destStorageNode.exists:
            counter += 1
            destname = '%s_%02i' %(destname,counter)
            destStorageNode = self.parent.storageNode(destStorageNode.dirname,'%s.pdf' %destname)

        call_list = ['abiword', '--to=pdf', sourceStorageNode, '-o', destStorageNode]
        try:
            result = sourceStorageNode.service.call(call_list)
            if result !=0:
                return None
            return destStorageNode.fullpath
        except Exception:
            return None
        