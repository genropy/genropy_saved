# -*- coding: UTF-8 -*-

# remote.py
# Created by Francesco Porcari on 2011-05-01.
# Copyright (c) 2011 Softwell. All rights reserved.

"Test page description"
class GnrCustomWebPage(object):
    #py_requires="gnrcomponents/testhandler:TestHandlerFull"

    def windowTitle(self):
        return ''
         
    def test_0_firsttest(self,pane):
        """First test description"""
        pane.textbox(value='^.par')
        pane.div('^.pup')

       # pane.textbox(value='^.pup')
        pane.framePane('testone',height='100px',background='lime').remote('xxx',par='^.par',_if='par')
        
        pane.data('.pup','piero')
        
    def main_root(self,pane,**kwargs):
        pane.dataController().dataController("alert(pippo)",pippo="^pippo")
        pane.button('aaa',fire_pippo='pippo')


    def remote_xxx(self,pane,par=None):
        print 'pippo'
        fb = pane.formbuilder(cols=1, border_spacing='3px')
        fb.textbox(value='^.uuu',lbl=par)
        pane.dataFormula(".kkk", "u+p",u="^.uuu",p='=.par')
        fb.textbox(value='^.kkk',lbl='lll')
        