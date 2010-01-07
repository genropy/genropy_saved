#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#
#  untitled
#
#  Created by Giovanni Porcari on 2007-03-24.
#  Copyright (c) 2007 Softwell. All rights reserved.
#

import cups
from gnr.core.gnrbag import Bag
class GnrCustomWebPage(object):
    def pageAuthTags(self, method=None, **kwargs):
        return ''
        
    def windowTitle(self):
         return '!!'

    def main(self, root, **kwargs):
        root.data('printers', self.rpc_getPrinters())
        #root.dataRemote('printers', 'getPrinters', _init=True)
        root.data('selected_print','Select a mfck print')
        root.div('^selected_print').menu(storepath='printers',
                                          modifiers='*',
                                          action='SET selected_print = $1.fullpath;')
        #root.tree(storepath='printers')
        
    def rpc_getPrinters(self):
        printersBag=Bag()
        connection = cups.Connection()
        for printer_name, printer in connection.getPrinters().items():
            printersBag['%s.%s'%(printer['printer-location'],printer['printer-info'])]=printer_name
        return printersBag
        
        #pane.dataRemote('invoicablejobs_tree', 'invoicableJobsTree',
        #                 curr_div = '^_clientCtx.pforce.cur_division.code')
        #pane.tree(nodeId= 'modeTree',
        #          storepath='invoicablejobs_tree.tree',
        #          selectedPath='aux.job.condition_path',
        #          labelAttribute='caption', fired='^reloadTree')