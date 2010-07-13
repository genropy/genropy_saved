#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-

import datetime

class GnrCustomWebPage(object):
    def main(self, root, **kwargs):
        root.div('Hello assopy', font_size='40pt', border='3px solid yellow', 
                                            padding='20px')
        root.data('demo.today', self.toText(datetime.datetime.today()))
        root.div('^demo.today', font_size='20pt', border='3px solid yellow', 
                                            padding='20px', margin_top='5px')
        root.dataRpc('demo.hour', 'getTime', _fired='^updateTime', _init=True)
        hour=root.div(font_size='20pt', border='3px solid yellow',
                                            padding='20px', margin_top='5px' )  
        hour.span('^demo.hour')                                                                    
        hour.button('Update', fire='updateTime', margin='20px')
        
    def rpc_getTime(self):
        return self.toText(datetime.datetime.now(), format='HH:mm:ss')