#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#
#  untitled
#
#  Created by Giovanni Porcari on 2007-03-24.
#  Copyright (c) 2007 Softwell. All rights reserved.
#

""" Buttons """
import os
from gnr.core.gnrbag import Bag
from gnr.web.gnrwebpage import GnrWebPage

# --------------------------- GnrWebPage subclass ---------------------------
class GnrCustomWebPage(object):

    def main(self, root, **kwargs):
        #root = self.rootLayoutContainer(root)
        root.dataRemote('tables','app.getTablesTree',sync=True)
        #root.dataRemote('relations','app.getTableFields',table='^selectedTable',sync=True, _if='table')
        root.dataRemote('anag','app.getTableFields',table='utils.anagrafiche',sync=True)
       #x=root.dropdownbutton('test',name='b')
       #x=x.menu(action="function(x){alert('Selected:'+x.label)}",selected='xxx')
       #x.menuline('Do This')
       #x.menuline('Do That',action="alert('Doing That')")
       #p=x.menuline('Print to').menu()
       #p.menuline('Printer')
       #p.menuline('Fax')
       #p.menuline('-')
       #p.menuline('File')
       #x.menuline('-')
       #x.menuline('Do nothing')
        x=root.dropdownbutton('Table').menu(_class='gnrmenuscroll',storepath='tables',selected_tableid='selectedTable')
        #x=root.dropdownbutton('Field').menu(storepath='relations',selected='selectedField')
        x=root.dropdownbutton('Anagrafiche').menu(_class='gnrmenuscroll',storepath='anag',selected_fullpath='selectedFieldAnagrafiche')
def index(req, **kwargs):
    return GnrWebPage(req, GnrCustomWebPage, __file__, **kwargs).index()
