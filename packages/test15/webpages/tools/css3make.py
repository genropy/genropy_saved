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
        sl = pane.slotBar('deg,fld,tan,*,test,*,test1,*')
        
        sl.deg.verticalSlider(value='^.deg',minimum=0,maximum=360,intermediateChanges=True,height='100px')
        fb = sl.fld.formbuilder(cols=6, border_spacing='2px')
        fb.numbertextbox(value='^.deg',lbl='deg')
        sl.test.div(margin='5px', display='inline-block',
                 border='1px solid gray', width='100px', height='80px',
                 gradient_from='white',gradient_to='navy',gradient_degrees='^.deg')
                 
        sl.test1.div(margin='5px', display='inline-block',
                border='1px solid gray', width='100px', height='80px',
                gradient_color_0='pink,15',gradient_color_1='yellow,50' ,gradient_color_2='red,100',gradient_degrees='^.deg')
       
    def test_4_transform(self, pane):
        sl = pane.slotBar('rotate,translatex,translatey,scalex,scaley,skewx,skewy,*,test,*')
        sl.rotate.verticalSlider(value='^.rotate',minimum=0,maximum=360,intermediateChanges=True,height='100px',default_value=0)
        sl.translatex.verticalSlider(value='^.translate_x',minimum=-100,maximum=100,intermediateChanges=True,height='100px',default_value=0)
        sl.translatey.verticalSlider(value='^.translate_y',minimum=-100,maximum=100,intermediateChanges=True,height='100px',default_value=0)
        sl.scalex.verticalSlider(value='^.scale_x',minimum=0,maximum=1,intermediateChanges=True,height='100px',default_value=1)
        sl.scaley.verticalSlider(value='^.scale_y',minimum=0,maximum=1,intermediateChanges=True,height='100px',default_value=1)
        sl.skewx.verticalSlider(value='^.skew_x',minimum=0,maximum=360,intermediateChanges=True,height='100px',default_value=0)
        sl.skewy.verticalSlider(value='^.skew_y',minimum=0,maximum=360,intermediateChanges=True,height='100px',default_value=0)
        sl.test.div(margin='5px', display='inline-block', border='1px solid gray', width='50px', height='70px'
                 ,transform_rotate='^.rotate'
                 ,transform_translate_x='^.translate_x',transform_translate_y='^.translate_y'
                 ,transform_scale_x='^.scale_x',transform_scale_y='^.scale_y'
                 ,transform_skew_x='^.skew_x',transform_skew_y='^.skew_y'
                 )
