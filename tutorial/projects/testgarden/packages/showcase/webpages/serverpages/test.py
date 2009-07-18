#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#

from gnr.web.gnrwsgipage import GnrHtmlPage as page_factory


class GnrCustomWebPage(object):
    def main(self, body, name='World'):

        body.div('Hello,')
        body.div('%s!'%name, style='color:red;')
        tbl = body.table()
        for i in range(10):
            tr = tbl.tr()
            for j in range(10):
                tr.td('%s.%s'%(i,j))
        

