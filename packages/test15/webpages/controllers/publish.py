# -*- coding: UTF-8 -*-

# publish.py
# Created by Francesco Porcari on 2010-09-30.
# Copyright (c) 2010 Softwell. All rights reserved.

class GnrCustomWebPage(object):
    py_requires="gnrcomponents/testhandler:TestHandlerBase"

    def windowTitle(self):
        return 'Publish'
         
    def test_1_publish_subscribe(self,pane):
        pane.textbox(value='^test')
        pane.button('publish',action='genro.publish("pressed",arg,"miao")',arg='=test')
        pane.dataController("console.log(pressed[0]); console.log(pressed[1]);",
                            subscribe_pressed=True)
        #pane.div(subscribe_test_pressed='var args =arguments; genro.bp(args);')
    
    def test_2_publish_subscribe_button(self,pane):
        pane.button('publish',action='PUBLISH pressed_2 = "bau","miao";')
        pane.dataController("console.log(pressed_2[0]); console.log(pressed_2[1]);",
                            subscribe_pressed_2=True)
