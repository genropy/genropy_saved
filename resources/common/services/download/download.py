#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#
#  Created by Saverio Porcari on 2013-04-06.
#  Copyright (c) 2013 Softwell. All rights reserved.


from gnr.core.gnrbaseservice import GnrBaseService                                                  
import urllib2
import os


class Main(GnrBaseService):
    def __init__(self,parent,**kwargs):
        self.parent = parent

    def __call__(self,url,destinationFolder=None,file_name=None):
        #url = "http://download.thinkbroadband.com/10MB.zip"
        file_name = file_name or url.split('/')[-1]
        u = urllib2.urlopen(url)
        destinationFolder = destinationFolder or 'site:download'
        if ':' in destinationFolder:
            filepath = self.parent.getStaticPath(destinationFolder,file_name,autocreate=-1)
        else:
            filepath = os.path.join(destinationFolder,file_name)
        with open(os.path.join(filepath), 'wb') as f:
            meta = u.info()
            file_size = int(meta.getheaders("Content-Length")[0])
            print "Downloading: %s Bytes: %s" % (file_name, file_size)
            file_size_dl = 0
            block_sz = 8192
            while True:
                buffer = u.read(block_sz)
                if not buffer:
                    break
                file_size_dl += len(buffer)
                f.write(buffer)
                status = r"%10d  [%3.2f%%]" % (file_size_dl, file_size_dl * 100. / file_size)
                status = status + chr(8)*(len(status)+1)
                print status,
            f.close()
        return filepath