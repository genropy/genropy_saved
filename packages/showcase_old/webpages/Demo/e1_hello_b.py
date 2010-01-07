#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-

import datetime


class GnrCustomWebPage(object):
    
    def main(self, root, **kwargs):
        root.div('Hello assopy', font_size='40pt', 
                        border='3px solid yellow', padding='20px')
                        
        root.data('demo.today', datetime.date.today())
        root.dateTextBox(value='^demo.today')
        
        root.div('^demo.today', font_size='20pt', border='3px solid yellow', 
                                padding='20px', margin_top='5px', format='long')

