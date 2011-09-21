# -*- coding: UTF-8 -*-

# toolbar.py
# Created by Filippo Astolfi on 2011-03-22.
# Copyright (c) 2011 Softwell. All rights reserved.

"""slotBar and slotToolbar"""

import datetime

class GnrCustomWebPage(object):
    py_requires = """gnrcomponents/testhandler:TestHandlerFull,
                     foundation/includedview"""
                     
    def windowTitle(self):
        return 'slotBar and slotToolbar'
        
    def test_1_features(self,pane):
        """framePane, slotToolbar and CSS 3"""
        workdate = str(datetime.datetime.now().date())
        pane.data('.color','white')
        pane.data('.from','#4BA21A')
        pane.data('.to','#7ED932')
        pane = pane.framePane(frameCode='test2',height='400px',
                              shadow='3px 3px 5px gray',rounded=10,
                              border='1px solid #bbb',margin='10px',
                              center_background='#E1E9E9')
        top = pane.top.slotToolbar(slots='10,hello,*,foo,*,dummy,export,searchOn',
                                   height='25px',gradient_from='^.from',gradient_to='^.to')
        #view = pane.includedView(_newGrid=True)
        #struct = view.gridStruct('name')
        #view.selectionStore(table='showcase.person',order_by='$name',
        #                    _onStart=True,storeCode='mystore')
        #top.hello.div(workdate,color='^.color')
        #top.foo.div('Schedule',font_size='14pt',color='^.color')
        #top.dummy.button(label='add',iconClass='icnBaseAdd',showLabel=False,
        #                 action="alert('Added a row in your grid')")
        #top.dummy.button(label='del',iconClass='icnBaseDelete',showLabel=False,
        #                 action="alert('Deleted a row in your grid')")
        #top.dummy.button(label='email',iconClass='icnBaseEmail',showLabel=False,
        #                 action="alert('Sended your schedule by email')")
        #top.dummy.button(label='pdf',iconClass='icnBasePdf',showLabel=False,
        #                 action="alert('PDF created')")
        #top.dummy.button(label='print',iconClass='icnBasePrinter',showLabel=False,
        #                 action="alert('Printed')")
        
        left = pane.left.slotBar(slotbarCode='left',slots='10,foo,*',width='40px',
                                 gradient_from='^.from',gradient_to='^.to',gradient_deg='0')
        left.foo.button('new grid',action="alert('New schedule')")
        left.foo.button('save grid',action="alert('Saved')")
        left.foo.button('load grid',action="alert('Loaded')")
        left.foo.button('exit', action="alert('Exited')")
        
        right = pane.right.slotBar(slotbarCode='right',slots='20,dummy,*',width='130px',
                                   gradient_from='^.from',gradient_to='^.to',gradient_deg='^.deg')
        fb = right.dummy.formbuilder(lbl_color='^.color',cols=2)
        fb.div('Settings',font_size='12pt',color='^.color',colspan=2)
        fb.comboBox(lbl='color',value='^.color',width='90px',colspan=2,
                    values="""aqua,black,blue,fuchsia,gray,green,lime,maroon,
                              navy,olive,purple,red,silver,teal,white,yellow
                              """) # A complete list of CSS 3 basic color keywords
        fb.filteringSelect(lbl='from',value='^.from',width='90px',colspan=2,
                           values="""#0065E7:dark Blue,#4BA21A:dark Green,
                                     #E3AA00:dark Orange,#C413A9:dark Pink,
                                     #960000:Dark Red""")
        fb.filteringSelect(lbl='to',value='^.to',width='90px',colspan=2,
                           values="""#29DFFA:light Blue,#7ED932:light Green,
                                     #F4DC7F:light Orange,#FFCCED:light Pink,
                                     #FD4042:light Red""")
        fb.verticalSlider(value='^.deg',minimum=0,maximum=360,discreteValues=361,
                          intermediateChanges=True,height='100px',lbl='Deg')
        fb.numbertextbox(value='^.deg',lbl='deg',width='3em')
        
        bottom = pane.bottom.slotToolbar(slots='300,bar,*',height='20px',
                                         gradient_from='^.from',gradient_to='^.to')
        bottom.bar.div('Here goes the messages for user',color='^.color')
        
        #sb = frame.div('Remember: a slotToolbar (or a slotBar) can be attached to any div!',
        #                margin='20px',color='black').slotToolbar(slotbarCode='top',slots='10,hello,*,dummy',
        #                                                         height='25px',gradient_from='^.from',gradient_to='^.to')
        #sb.hello.button('Click me!',action='alert("Hello!!!")')
        #sb.dummy.button(label='',iconClass='icnBasePref',showLabel=False,
        #                action="alert('A wonderful action!')")
        #frame.div('Here goes the \"center\" content.',margin='20px')
        
    def test_2_div(self,pane):
        """slotToolbar and toolBar attached on a div"""
        pane.div('You can attach a toolbar to any div:')
        top = pane.div().slotToolbar(slotbarCode='top',slots='hello,foo,dummy',
                                     gradient_from='red',gradient_to='white')
        top.hello.div('Hello!')
        top.foo.div('MyTitle',font_size='14pt',color='^.color')
        top.dummy.button(label='add',iconClass='icnBaseAdd',action="alert('Added!')")
        
        pane.div().slotBar(slotbarCode='yeah',slots='hello,*,hello2',
                           gradient_from='purple',gradient_to='white',
                           gradient_degree='36')