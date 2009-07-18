#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#

from gnr.web.gnrwsgipage import GnrHtmlPage as page_factory


class GnrCustomWebPage(object):

    def main(self, body, name='World'):
        self.dojo(version='11')
        self.gnr_css()
        root=body.div(_class='tundra')
        root.script("""dojo.require("dijit.form.DateTextBox");""")
        root.div('Hello,')
        root.div('%s!'%name, style='color:red;')
        root.input(_type="text", 
                   dojoType='dijit.form.DateTextBox',
                   id="mydate",name='mydate')
        root.label(_for='mydate',content="my date")
        

        #tbl = body.table()
        #for i in range(100):
        #    tr = tbl.tr()
        #    for j in range(100):
        #        tr.td('%s.%s'%(i,j))
        

