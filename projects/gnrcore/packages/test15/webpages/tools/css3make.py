# -*- coding: UTF-8 -*-
# 
"""css3make tester"""

class GnrCustomWebPage(object):
    py_requires = "gnrcomponents/testhandler:TestHandlerBase"
    dojo_theme = 'tundra'
    def test_1_rounded(self, pane):
        sl = pane.slotBar('fld,test,*')
        fb = sl.fld.formbuilder(cols=2,lbl_position='L',
                                lbl_font_size='10px',lbl_color='teal')
        fb.horizontalSlider(value='^.top_left',minimum=0,maximum=30,
                            intermediateChanges=True,width='150px',
                            discreteValues=31,lbl='top_left')
        fb.numbertextbox(value='^.top_left',width='4em')
        fb.horizontalSlider(value='^.top_right',minimum=0,maximum=30,
                            intermediateChanges=True,width='150px',
                            discreteValues=31,lbl='top_right')
        fb.numbertextbox(value='^.top_right',width='4em')
        fb.horizontalSlider(value='^.bottom_left',minimum=0,maximum=30,
                            intermediateChanges=True,width='150px',
                            discreteValues=31,lbl='bottom_left')
        fb.numbertextbox(value='^.bottom_left',width='4em')
        fb.horizontalSlider(value='^.bottom_right',minimum=0,maximum=30,
                            intermediateChanges=True,width='150px',
                            discreteValues=31,lbl='bottom_right')
        fb.numbertextbox(value='^.bottom_right',width='4em')
        sl.test.div(margin='5px',margin_left='100px',display='inline-block',
                    border='1px solid gray',width='200px',height='80px',
                    rounded_top_left='^.top_left',
                    rounded_top_right='^.top_right',
                    rounded_bottom_left='^.bottom_left',
                    rounded_bottom_right='^.bottom_right')
        
    def test_2_shadow(self, pane):
        sl = pane.slotBar('x,y,blur,color,inset,*,test1,*',
                          lbl_font_size='10px',lbl_width='12px',
                          lbl_position='L',lbl_transform_rotate='-90',lbl_color='teal',
                          cell_border='1px dotted gray')
        sl.x.verticalSlider(value='^.x',minimum=-30,maximum=30,intermediateChanges=True,
                            height='100px',lbl='X')
        sl.y.verticalSlider(value='^.y',minimum=-30,maximum=30,intermediateChanges=True,
                            height='100px',lbl='Y')
        sl.blur.verticalSlider(value='^.blur',minimum=-30,maximum=30,intermediateChanges=True,
                               height='100px',lbl='blur')
        sl.color.comboBox(value='^.color',width='90px',lbl='color',
                          values="""aqua,black,blue,fuchsia,gray,green,lime,maroon,
                                    navy,olive,purple,red,silver,teal,white,yellow
                                    """)
        sl.inset.checkbox(value='^.inset',label='shadow_inset')
        sl.test1.div(margin='5px',display='inline-block',border='1px solid gray',
                     width='100px', height='80px',shadow='3px 3px 5px gray inset',
                     shadow_x='^.x',shadow_y='^.y',shadow_blur='^.blur',
                     shadow_color='^.color',shadow_inset='^.inset')
        
    def test_3_gradient(self, pane):
        sl = pane.slotBar('deg,fld,*,test,*,test1,*',lbl_position='B',lbl_font_size='8px')
        sl.deg.verticalSlider(value='^.deg',minimum=0,maximum=360,default=10,
                              intermediateChanges=True,height='100px',lbl='Deg')
        fb = sl.fld.formbuilder(cols=6, border_spacing='2px')
        fb.data('.from','#4BA21A')
        fb.data('.to','#7ED932')
        fb.numbertextbox(value='^.deg',lbl='deg',width='4em')
        fb.filteringSelect(lbl='from',value='^.from',width='90px',colspan=2,
                           values="""#0065E7:dark Blue,#4BA21A:dark Green,
                                     #E3AA00:dark Orange,#C413A9:dark Pink,
                                     #960000:Dark Red""")
        fb.filteringSelect(lbl='to',value='^.to',width='90px',colspan=2,
                           values="""#29DFFA:light Blue,#7ED932:light Green,
                                     #F4DC7F:light Orange,#FFCCED:light Pink,
                                     #FD4042:light Red""")
        sl.test.div(margin='5px', display='inline-block',
                    border='1px solid gray',width='100px',height='80px',
                    gradient_from='^.from',gradient_to='^.to',gradient_deg='^.deg')
        sl.test1.div(margin='5px', display='inline-block',
                     border='1px solid gray', width='100px', height='80px',
                     gradient_color_0='pink,15',gradient_color_1='yellow,50',gradient_color_2='red,100',
                     gradient_deg='^.deg')
                     
    def test_4_transform(self, pane):
        sl = pane.slotBar('fld,*,test,*')
        fb = sl.fld.formbuilder(lbl_font_size='10px',lbl_color='teal')
        fb.horizontalSlider(value='^.rotate',minimum=0,maximum=180,lbl='rotate',
                            intermediateChanges=True,width='150px',default_value=0)
        fb.horizontalSlider(value='^.translate_x',minimum=-100,maximum=100,lbl='translate_x',
                            intermediateChanges=True,width='150px',default_value=0)
        fb.horizontalSlider(value='^.translate_y',minimum=-100,maximum=100,lbl='translate_y',
                            intermediateChanges=True,width='150px',default_value=0)
        fb.horizontalSlider(value='^.scale_x',minimum=0,maximum=1,lbl='scale_x',
                            intermediateChanges=True,width='150px',default_value=1)
        fb.horizontalSlider(value='^.scale_y',minimum=0,maximum=1,lbl='scale_y',
                            intermediateChanges=True,width='150px',default_value=1)
        fb.horizontalSlider(value='^.skew_x',minimum=0,maximum=360,lbl='skew_x',
                            intermediateChanges=True,width='150px',default_value=0)
        fb.horizontalSlider(value='^.skew_y',minimum=0,maximum=360,lbl='skew_y',
                            intermediateChanges=True,width='150px',default_value=0)
        sl.test.div(margin='100px',display='inline-block',border='1px solid gray',width='90px',height='120px',
                    transform_rotate='^.rotate',
                    transform_translate_x='^.translate_x',transform_translate_y='^.translate_y',
                    transform_scale_x='^.scale_x',transform_scale_y='^.scale_y',
                    transform_skew_x='^.skew_x',transform_skew_y='^.skew_y')
                    
    def test_5_transition(self, pane):
        sl = pane.slotBar('w,color,mode,duration,*,test',lbl_position='T',
                           lbl_font_size='10px',lbl_color='teal')
        sl.w.textbox(value='^.w',lbl='width',default='3px',width='5em')
        sl.color.textbox(value='^.color',lbl='color',default='red',width='6em')
        sl.mode.combobox(value='^.function',default='linear',width='8em',
                         values='linear,ease,ease-in,ease-out,ease-in-out')
        sl.duration.numbertextbox(lbl='duration',default=2,value='^.duration',width='8em')
        sl.test.div(width='^.w',background='^.color',height='50px',border='1px solid gray',
                    transition='all 3s',transition_function='.^function',transition_duration='^.duration')
