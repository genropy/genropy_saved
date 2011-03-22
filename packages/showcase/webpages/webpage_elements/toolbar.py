# -*- coding: UTF-8 -*-

# toolbar.py
# Created by Filippo Astolfi on 2011-03-22.
# Copyright (c) 2011 Softwell. All rights reserved.

"""slotBar and slotToolbar"""

import datetime

class GnrCustomWebPage(object):
    py_requires = 'gnrcomponents/testhandler:TestHandlerFull'
    dojo_theme = 'soria'
    
    def windowTitle(self):
         return 'slotBar and slotToolbar'
         
    def _test_1_simple(self,pane):
        """simple example"""
        workdate = str(datetime.datetime.now().date())
        frame = pane.framePane(frameCode='dummy',height='150px',margin='10px',
                               center_background='gray',rounded=10,design='headline') # design='sidebar'
        top = frame.top.slotToolbar(slotbarCode='dummy1',slots='*,foo,*',height='20px')
        top.foo.div('Hello!')
        left = frame.left.slotToolbar(slotbarCode='dummy2',slots='*,foo,*',width='30px')
        left.foo.div('Left Hello!')
        right = frame.right.slotToolbar(slotbarCode='dummy3',slots='*,foo,*',width='30px')
        right.foo.div('Right Hello!')
        bottom = frame.bottom.slotBar(slotCode='dummy8',slots='*,foo,*',height='20px')
        bottom.foo.div('Hello! (from the bottom slotBar)')
        
    def test_2_features(self,pane):
        """Some added features"""
        workdate = str(datetime.datetime.now().date())
        pane.data('color','yellow')
        pane.data('from','#4BA21A')
        pane.data('to','#7ED932')
        
        frame = pane.framePane(frameCode='framecode',height='400px',
                               shadow='3px 3px 5px gray',rounded=10,
                               border='1px solid #bbb',margin='10px',
                               center_background='#E1E9E9')
        top = frame.top.slotToolbar(slotbarCode='top',slots='10,hello,*,foo,*,dummy',
                                    height='25px',gradient_from='^from',gradient_to='^to')
        top.hello.div(workdate,color='^color')
        top.foo.div('Schedule',font_size='14pt',color='^color')
        top.dummy.button(label='add',iconClass='icnBaseAdd',showLabel=False,
                         action="alert('Added a row in your grid')")
        top.dummy.button(label='del',iconClass='icnBaseDelete',showLabel=False,
                         action="alert('Deleted a row in your grid')")
        top.dummy.button(label='email',iconClass='icnBaseEmail',showLabel=False,
                         action="alert('Sended your schedule by email')")
        top.dummy.button(label='pdf',iconClass='icnBasePdf',showLabel=False,
                         action="alert('PDF created')")
        top.dummy.button(label='print',iconClass='icnBasePrinter',showLabel=False,
                         action="alert('Printed')")
                         
        left = frame.left.slotToolbar(slotbarCode='left',slots='10,foo,*',width='40px',
                                      gradient_from='^from',gradient_to='^to')
        left.foo.button('new grid',action="alert('New schedule!')")
        left.foo.button('save grid',action="alert('Saved!')")
        left.foo.button('load grid',action="alert('Loaded!')")
        left.foo.button('exit', action="alert('Exited!')")
        
        right = frame.right.slotToolbar(slotbarCode='left',slots='20,dummy,*',
                                        width='200px',gradient_from='^from',gradient_to='^to')
        fb = right.dummy.formbuilder(lbl_color='^color')
        fb.div('Settings',font_size='12pt',color='^color')
        fb.comboBox(lbl='color',values='black,white,yellow',value='^color',width='90px')
        fb.filteringSelect(lbl='gradient_from',value='^from',width='90px',
                           values="""#0065E7:dark Blue,#4BA21A:dark Green,
                                     #E3AA00:dark Orange,#C413A9:dark Pink,
                                     #960000:Dark Red""")
        fb.filteringSelect(lbl='gradient_to',value='^to',width='90px',
                           values="""#29DFFA:light Blue,#7ED932:light Green,
                                     #F4DC7F:light Orange,#FFCCED:light Pink,
                                     #FD4042:light Red""")
        
        bottom = frame.bottom.slotToolbar(slots='300,bar,*,searchOn',height='20px',
                                          gradient_from='^from',gradient_to='^to')
        bottom.bar.div('Here goes the messages for user',color='^color')
        
        frame.div('Here goes the \"center\" content',margin='20px')
                           