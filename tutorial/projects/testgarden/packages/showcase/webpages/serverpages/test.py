#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#

from gnr.web.gnrhtmlpage import GnrHtmlPage as page_factory


class GnrCustomWebPage(object):
    def main(self, body, name='World'):
        body.div('Hello,')
        body.div('%s!'%name, color='red;')
        tbl = body.table(background_color='lime')
        for i in range(10):
            tr = tbl.tr()
            for j in range(10):
                tr.td('%s.%s'%(i,j))
        

