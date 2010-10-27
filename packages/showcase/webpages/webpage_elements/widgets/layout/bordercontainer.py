# -*- coding: UTF-8 -*-

# border.py
# Created by Filippo Astolfi on 2010-09-01.
# Copyright (c) 2010 Softwell. All rights reserved.

"""Border Container"""

from gnr.core.gnrbag import Bag

class GnrCustomWebPage(object):
    py_requires="gnrcomponents/testhandler:TestHandlerFull"
    # dojo_theme='claro'    # !! Uncomment this row for Dojo_1.5 usage
    
    # For an exhaustive documentation, please see http://docs.genropy.org/widgets/layout/bordercontainer.html
    
    def test_1_basic(self,pane):
        """Basic example"""
        bc = pane.borderContainer(height='400px')
        top = bc.contentPane(region='top',height='5em',background_color='#f2c922')
        top.div('Specify my height!',font_size='.9em',text_align='justify',margin='10px')
        center = bc.contentPane(region='center',background_color='silver',padding='10px')
        center.div("""Like in Dojo, this widget is a container partitioned into up to five regions:
                      left (or leading), right (or trailing), top, and bottom with a mandatory center
                      to fill in any remaining space. Each edge region may have an optional splitter
                      user interface for manual resizing.""",
                      font_size='.9em',text_align='justify',margin='10px')
        center.div("""Sizes are specified for the edge regions in pixels or percentage using CSS – height
                      to top and bottom, width for the sides. You have to specify the "height" attribute
                      for the "top" and the "bottom" regions, and the "width" attribute for the "left" and
                      "right" regions. You shouldn’t set the size of the center pane, since it’s size is determined
                      from whatever is left over after placing the left/right/top/bottom panes.)""",
                      font_size='.9em',text_align='justify',margin='10px')
        left = bc.contentPane(region='left',width='130px',background_color='red',splitter=True)
        left.div('Specify my width!',font_size='.9em',text_align='justify',margin='10px')
        right = bc.contentPane(region='right',width='130px',background_color='yellow')
        right.div('Specify my width!',font_size='.9em',text_align='justify',margin='10px')
        bottom = bc.contentPane(region='bottom',height='80px',background_color='grey')
        bottom.div('Specify my height!',font_size='.9em',text_align='justify',margin='10px')
        
    def test_2_advanced(self,pane):
        """Advanced example"""
        pane.data('width_top',40)
        pane.data('width_left',100)
        pane.data('regions.top',show=False)
        pane.data('regions.left?show',False)
        pane.dataFormula('regions.top','w+umw',w='^width_top',umw='^um_width_top')
        pane.dataFormula('regions.left','w+umw',w='^width_left',umw='^um_width_left')
        
        bc = pane.borderContainer(height='500px')
        top = bc.contentPane(region='top',height='100px')
        fb = top.formbuilder(cols=4)
        fb.div("""With the "regions" attribute you can add the "show" attribute
                   to the borderContainer and its regions.""",
                   colspan=4,background_color='silver',margin_bottom='5px')
        
        fb.checkbox(value='^regions.top?show',label='Show top pane')
        fb.numberTextbox(value='^width_top',width='4em',places=2)
        fb.horizontalSlider(value='^width_top',width='200px',minimum=0,maximum=400,
                            intermediateChanges=True,lbl='Change top pane dimension')
        fb.comboBox(value='^um_width_top',width='5em',values='em,px',default='px')
        
        fb.checkbox(value='^regions.left?show',label='Show left pane')
        fb.numberTextbox(value='^width_left',width='4em',places=2)
        fb.horizontalSlider(value='^width_left',width='200px',minimum=0,maximum=850,
                            intermediateChanges=True,lbl='Change left pane dimension')
        fb.comboBox(value='^um_width_left',width='5em',values='em,px',default='px')
        
        bc2 = bc.borderContainer(region='center',regions='^regions')
        top2 = bc2.contentPane(region='top',height='40px',background_color='#f2c922')
        left2 = bc2.contentPane(region='left',width='100px',background_color='orange')
        center2 = bc2.contentPane(region='center',background_color='silver',padding='10px')
        center2.div("""In this sample there are two buttons that can make visible the left and the top
                       contentPane(s), two numberTextbox(es) that show the actual dimension of top
                       and left panes, two horizontalSliders with which you can modify the dimensions of
                       top and left pane and a comboBox that allow you to change from "px" to "em".""",
                       font_size='.9em',text_align='justify',margin='10px')
                       