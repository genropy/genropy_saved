#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#

from gnr.web.gnrwsgipage import GnrHtmlPage as page_factory


class GnrCustomWebPage(object):
    dojoversion='11'
    theme='soria'
    def main(self, body, name='World'):
        self.dojo()
        self.gnr_css()
        body.script("""dojo.require("dijit.form.DateTextBox");""")
        body.div('Hello,')
        body.div('%s!'%name, style='color:red;')
        body.input(_type="text", 
                   dojoType='dijit.form.DateTextBox',
                   id="mydate",name='mydate')
        body.label(_for='mydate',content="my text")
        

        #tbl = body.table()
        #for i in range(100):
        #    tr = tbl.tr()
        #    for j in range(100):
        #        tr.td('%s.%s'%(i,j))
        

