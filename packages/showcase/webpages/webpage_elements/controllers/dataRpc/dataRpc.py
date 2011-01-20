# -*- coding: UTF-8 -*-

# dataFormula.py
# Created by Filippo Astolfi on 2010-10-28.
# Copyright (c) 2010 Softwell. All rights reserved.

"""dataRpc"""

from time import sleep
import datetime

class GnrCustomWebPage(object):
    py_requires = "gnrcomponents/testhandler:TestHandlerFull"
    # dojo_theme='claro'    # !! Uncomment this row for Dojo_1.5 usage

    def test_1_basic(self, pane):
        """dataRpc"""
        pane.div('^demo.today', font_size='20pt', border='3px solid yellow', padding='20px', margin_top='5px')
        pane.data('demo.today', self.toText(datetime.datetime.today()))

        hour = pane.div(font_size='20pt', border='3px solid yellow', padding='10px', margin_top='5px')
        hour.span('^demo.hour')
        pane.dataRpc('demo.hour', 'getTime', _fired='^updateTime', _init=True)
        hour.button('Update', fire='updateTime', margin='20px')

    def rpc_getTime(self):
        return self.toText(datetime.datetime.now(), format='HH:mm:ss')

    def test_2_basic(self, root, **kwargs):
        """Area"""
        fb = root.formbuilder(cols=2)
        fb.data('base', 0)
        fb.data('height', 0)
        fb.horizontalSlider(lbl='!!Base', value='^base', width='200px', minimum=0, maximum=100,
                            intermediateChanges=True)
        fb.numberTextBox(value='^base', places=2)
        fb.horizontalSlider(lbl='!!Height', value='^height', width='200px', minimum=0, maximum=100,
                            intermediateChanges=True)
        fb.numberTextBox(value='^height', places=2)

        fb.dataFormula('area', 'base * height', base='^base', height='^height')

        fb.dataRpc('server_area', 'area', base='^base', height='^height',
                   _fired='^do_rpc', _if='_fired&&(base >= 0) && (height >= 0)',
                   _else='return "** No Server Call **"')

        fb.div(lbl='!!Area', value='^area', border='2px solid grey', padding='2px')
        fb.div(lbl='!!Rpc Area', value='^server_area', border='2px solid green', padding='2px')
        fb.div()
        fb.checkbox(value='^do_rpc', label='Calculated Server Area')

    def rpc_area(self, base, height):
        return base * height

    def test_3_basic(self, pane):
        """sync vs async"""
        pane.data('.x', 10)
        pane.data('.y', 10)
        #pane.button('Give me sync five',)
        #pane.div('^.result1')
        pane.button('Give me async five', action='SET .y=y-1; FIRE .async_five', y='=.y')
        pane.div('^.async5')
        #pane.dataRpc('.sync5','give_me_five',sync=True,_fired='^.sync_five',x='=.x')
        pane.dataRpc('.async5', 'give_me_five', _fired='^.async_five', y='=.y')

    def rpc_give_me_five(self, x=None, y=None, **kwargs):
        sleep(5)
        return y + 5
        