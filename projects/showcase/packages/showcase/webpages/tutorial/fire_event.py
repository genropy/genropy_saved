#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-

#  Created by Giovanni Porcari on 2007-03-24.
#  Copyright (c) 2007 Softwell. All rights reserved.

class GnrCustomWebPage(object):
    def main(self, root, **kwargs):
        root.data('labelDelBottone', 'pippo')
        root.data('disab', False)
        root.textbox(value='^valoredamettere')
        root.textbox(value='^labelDelBottone')
        root.checkbox(value='^disab')
        root.button('^labelDelBottone', action='SET miovalore=GET valoredamettere;', disabled='^disab')
        root.div('^miovalore', callAgain='^asdrubale')

        root.button('bottone 2', action='FIRE miovalore2=777;')
        root.div('^miovalore2', callAgain='^asdrubale')

        root.dataController('FIRE asdrubale', _timing=1)
        root.numberTextBox(value='^valoremio')
        root.dataRpc('risultato', 'doppio', valore='^valoremio')
        root.div('^risultato')
        root.dataFormula('risultato2', 'valore*2', valore='^valoremio')
        root.div('^risultato2')

    def rpc_doppio(self, valore=0):
        import time

        time.sleep(valore / 1000)
        return valore * 2