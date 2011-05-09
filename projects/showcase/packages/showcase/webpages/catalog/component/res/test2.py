#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-

#  Created by Giovanni Porcari on 2007-03-24.
#  Copyright (c) 2007 Softwell. All rights reserved.

class GnrCustomWebPage(object):
    def main(self, rootBC, **kwargs):
        rootBC.data('current', 'Piero')
        rootBC.div('Storage', storage='alert("a")')
        rootBC.div('^current.verdi')
        rootBC.div('^current.rossi')

        #rootBC.dataController("dojo.connect(sessionStorage,'setItem',function(e){console.log(e);})",_onStart=True)
        rootBC.dataController("SET current = sessionStorage.getItem('pippo');", _timing=.1)