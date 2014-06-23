# -*- coding: UTF-8 -*-

# hello.py
# Created by Francesco Porcari on 2010-08-19.
# Copyright (c) 2010 Softwell. All rights reserved.

"""hello"""

class GnrCustomWebPage(object):

    def main(self, root, **kwargs):
        frame = root.framePane(background='red')




        frame.dataController("genro.dlg.alert(pippo,pippo);",subscribe_dialog_open=True)
        bar = frame.bottom.slotBar('*,button_a,button_b,4')

        bar.button_a.slotButton('Azzera',action='genro.parentFrameNode().publish("azzera",{xxx:33})')

        bar.button_b.button('Duplica',action='genro.parentFrameNode().publish("duplica",{bar:"xxxx",foo:42});')