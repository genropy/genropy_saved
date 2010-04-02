#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#
#  untitled
#
#  Created by Giovanni Porcari on 2007-03-24.
#  Copyright (c) 2007 Softwell. All rights reserved.
#

import datetime

class GnrCustomWebPage(object):
    def windowTitle(self):
         return '!!Hello world'

    def main(self, root, **kwargs):
        tabber = root.tabContainer()
        tab = tabber.contentPane(title='Tab')
        tab.button('Che ore sono?',action='FIRE chiedi_ora;')
        root.dataRpc('risultato','dammi_ora',_fired='^chiedi_ora')
        tab.div('^risultato')
        
    def rpc_dammi_ora(self):
        return datetime.datetime.now()
