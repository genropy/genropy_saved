#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#
#  untitled
#
#  Created by Giovanni Porcari on 2007-03-24.
#  Copyright (c) 2007 Softwell. All rights reserved.
#

""" GnrDojo Hello World """
import os, datetime

from gnr.core.gnrbag import Bag

class GnrCustomWebPage(object):
    py_requires = 'public:Public,public:IncludedView'    
    
    def mainLeftContent(self,parentBC,**kwargs):
        pass
        
    def main(self, root, **kwargs):
        rootBC = root.borderContainer(**kwargs)
        bottom = rootBC.contentPane(height='4ex',background_color='red',region='bottom')
        center = rootBC.contentPane(region='center')
        iframe = center.iframe(src='^iframeurl',width='100%',height='100%',border='0')
        bottom.button('Set Url',action='SET iframeurl="gridinput.py?pippo=sss"')
        
            

