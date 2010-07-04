# -*- coding: UTF-8 -*-

# publish_subscribe.py
# Created by Francesco Porcari on 2010-07-04.
# Copyright (c) 2010 Softwell. All rights reserved.

class GnrCustomWebPage(object):
    #py_requires='public:Public'

    def pageAuthTags(self, method=None, **kwargs):
        return ''
        
    def windowTitle(self):
        return ''
         
    def main(self, root, **kwargs):
        root.button('publish',action='genro.publish("testTopic",4,"piero");')
        root.textbox(value='^pippo',subscribe_testTopic='SET pippo=$1;')