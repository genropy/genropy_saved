# -*- coding: UTF-8 -*-
# 
"""css3make tester"""

class GnrCustomWebPage(object):
    py_requires = "gnrcomponents/testhandler:TestHandlerBase"
    dojo_theme = 'tundra'

    def test_1_rounded(self, pane):
        sl = pane.slotBar('k,*,test,*')

        sl.k.verticalSlider(value='^.k',minimum=0,maximum='30',intermediateChanges=True,height='100px')
        test = sl.test.div(width='400px')
        test.div(margin='5px', display='inline-block', border='1px solid gray', width='100px', height='80px',
                 rounded='15')
        test.div(margin='5px', display='inline-block', border='1px solid gray', width='100px', height='80px',
                 rounded='12',rounded_left_top=0,rounded_bottom_right=0)
        test.div(margin='5px', display='inline-block', border='1px solid gray', width='100px', height='80px',
                 rounded_left_top='12',rounded_bottom_right='^.k')
    
    def test_2_shadow(self, pane):
        sl = pane.slotBar('x,y,blur,inset,*,test,*')
        sl.x.verticalSlider(value='^.x',minimum=-30,maximum=30,intermediateChanges=True,height='100px')
        sl.y.verticalSlider(value='^.y',minimum=-30,maximum=30,intermediateChanges=True,height='100px')
        sl.blur.verticalSlider(value='^.blur',minimum=-30,maximum=30,intermediateChanges=True,height='100px')
        sl.inset.checkbox(value='^.inset',label='Inset')
        sl.test.div(margin='5px', display='inline-block', border='1px solid gray', width='100px', height='80px',
                 shadow='3px 3px 5px gray inset',
                 shadow_x='^.x',shadow_y='^.y',
                 shadow_blur='^.blur',shadow_inset='^.inset')
      
    def test_3_gradient_fixed(self, pane):
        sl = pane.slotBar('deg,fld,tan,*,test,*')
        
        sl.deg.verticalSlider(value='^.deg',minimum=0,maximum=360,intermediateChanges=True,height='100px')
        fb = sl.fld.formbuilder(cols=6, border_spacing='2px')
        fb.numbertextbox(value='^.deg',lbl='deg')
        fb.numbertextbox(value='^.tng',lbl='tng')
        fb.numbertextbox(value='^.tng_corr',lbl='tng_corr')
        fb.textbox(value='^.result',lbl='res')
        fb.dataFormula(".tng", "Math.tan(d * Math.PI/180)",d='^.deg')
        fb.dataFormula(".tng_corr", "tng",tng='^.tng')
        fb.dataFormula(".tng_corr", "tng",tng='^.tng')
        fb.dataFormula(".result", "conCss2(d)",d='^.deg')

        pane.div(margin='5px', display='inline-block',
                 border='1px solid gray', width='100px', height='80px',
                 gradient_from='white',gradient_to='navy',gradient_degrees='^.deg')
    
                 

   #def test_3_gradient_fixed(self, pane):
   #    "firefox"
   #    sl = pane.slotBar('degrees,*,test,*')
   #    sl.degrees.verticalSlider(value='^.degrees',minimum=-90,maximum=90,intermediateChanges=True,height='100px')
   #    sl.test.div(margin='5px', display='inline-block', border='1px solid gray', width='100px', height='80px',
   #             gradient_from='gray',gradient_to='white',
   #             gradient_degrees='30')