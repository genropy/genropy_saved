#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#
#  Created by Saverio Porcari on 2013-04-06.
#  Copyright (c) 2013 Softwell. All rights reserved.


from gnr.core.gnrbaseservice import GnrBaseService
from subprocess import call
import os


class Main(GnrBaseService):
    def __init__(self, parent=None):
        self.parent = parent

    def convert(self,src_path, dest_path=None):
        if not dest_path:
            dirname, basename = os.path.split(src_path)
            dest_dir = os.path.join(dirname, 'converted_pdf')
            print dest_dir
            if not os.path.exists(dest_dir):
                os.makedirs(dest_dir)
            dest_name = '%s.pdf'%os.path.splitext(basename)[0]
            dest_path = os.path.join(dest_dir, dest_name)
        name,ext = os.path.splitext(dest_path)
        counter = 0
        while os.path.exists(dest_path):
            dest_path = '%s_%i%s'%(name,counter,ext)
            counter +=1
        return_path = dest_path
        if not os.path.isabs(src_path):
            src_path = self.parent.getStaticPath('site:%s'%src_path, autocreate=-1)
            dest_path = self.parent.getStaticPath('site:%s'%dest_path, autocreate=-1)
        call_list = ['abiword', '--to=pdf', src_path, '-o', dest_path]
        print call_list
        try:
            result = call(call_list)
            if result !=0:
                return None
            return return_path
        except Exception:
            return None
        