#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-

#  Created by Giovanni Porcari on 2007-03-24.
#  Copyright (c) 2007 Softwell. All rights reserved.

import datetime

class GnrCustomWebPage(object):
    def main(self, root, **kwargs):
        root.numbertextbox(value='^testo')
        root.button('What is the time?', action='FIRE get_time;')
        root.dataRpc('result', 'giveMeTime', _fired='^get_time',testo='^testo')
        root.div('^result')

    def rpc_giveMeTime(self,testo=''):
        return '%s : %s'  % (testo,str(datetime.datetime.now()))