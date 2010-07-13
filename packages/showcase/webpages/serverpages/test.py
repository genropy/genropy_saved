#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-

from gnr.web.gnrhtmlpage import GnrHtmlPage as page_factory

class GnrCustomWebPage(object):
    def main(self, body, name='World'):
        self.page_head(self.builder.head)
        
        body.div('Hello,')
        body.div('%s!'%name, color='red;')
        tbl = body.table(background_color='lime')
        for i in range(10):
            tr = tbl.tr()
            for j in range(10):
                tr.td('%s.%s'%(i,j))
                
    def page_head(self,head):
        head.meta( content="text/html; charset=UTF-8")
        head.meta(name="OWNER",content="Centro medico Euriclea")
        head.meta(name="AUTHOR", content="Paolo Camera,Matteo Gaiani")
        head.meta(name="Description", content="GenroMed software")
        head.meta(http_equiv="Content-Language" ,content="it")
        head.comment('<link rel="shortcut icon" href="favicon.ico">')
        head.meta(name="keywords", content="software, gestionale, medico")
        head.title('GenroMed')