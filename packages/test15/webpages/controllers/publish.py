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
        pane.dataController("console.log(arguments);console.log(pressed[0]); console.log(pressed[1]);",
                            subscribe_pressed=True)
        #pane.div(subscribe_test_pressed='var args =arguments; genro.bp(args);')
    
    def test_2_publish_subscribe_button(self,pane):
        pane.button('publish',action='PUBLISH pressed_2 = "bau","miao";')
        pane.dataController("console.log(pressed_2[0]); console.log(pressed_2[1]);",
                            subscribe_pressed_2=True)

    def test_3_publish_double_subscription(self,pane):
        pane.button('publish a',action='PUBLISH pressed_a = "bau","miao"')
        pane.button('publish b',action='PUBLISH pressed_b;')
        pane.dataController("if(_reason=='pressed_a'){console.log('you pressed a '+pressed_a[0])}else{console.log('you pressed b '+pressed_b[0])}",
                            subscribe_pressed_a=True,subscribe_pressed_b=True)
