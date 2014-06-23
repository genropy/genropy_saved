# -*- coding: UTF-8 -*-

# publish.py
# Created by Francesco Porcari on 2010-09-30.
# Copyright (c) 2010 Softwell. All rights reserved.

"""publish"""

class GnrCustomWebPage(object):
    py_requires = "gnrcomponents/testhandler:TestHandlerBase"

    def windowTitle(self):
        return 'Publish'

    def test_1_publish_subscribe(self, pane):
        pane.textbox(value='^test')
        pane.button('publish', action='genro.publish("pressed",mypar,"foo")', mypar='=test', nodeId='BUTTON_1')
        #the button use genro.publish to 'send a generic message' 'pressed' with par mypar and 'foo'
        pane.dataController("""console.log('I receved subscription "pressed" ');
                               console.log('first par was:'+pressed[0]);
                               console.log('second par was:'+pressed[1]);""",
                            subscribe_pressed=True)
        # the data controlller is triggered by subscribe_pressed and receives an array 'pressed' that
        # contains the published parameters
        #pane.div(subscribe_test_pressed='var args =arguments; genro.bp(args);')

    def test_2_publish_subscribe_button(self, pane):
        pane.button('publish', action='PUBLISH pressed_2 = "bau","miao";')
        pane.dataController("console.log(pressed_2[0]); console.log(pressed_2[1]);",
                            subscribe_pressed_2=True)

    def test_3_publish_double_subscription(self, pane):
        pane.button('publish a', action='PUBLISH pressed_a = "bau","miao"')
        pane.button('publish b', action='PUBLISH pressed_b;')
        pane.dataController(
                "if(_reason=='pressed_a'){console.log('you pressed a '+pressed_a[0])}else{console.log('you pressed b '+pressed_b[0])}"
                ,
                subscribe_pressed_a=True, subscribe_pressed_b=True)
