# -*- coding: UTF-8 -*-
"""framePane"""

import datetime

class GnrCustomWebPage(object):
    py_requires = 'gnrcomponents/testhandler:TestHandlerFull'
    workdate = datetime.datetime.now().date()
    
    def test_1_basic(self, pane):
        """Basic example"""
        frame = pane.framePane(frameCode='test1', design='headline',
                               height='400px', width='855px', shadow='3px 3px 5px gray',
                               rounded=5, border='1px solid #bbb', margin='10px',
                               center_border='1px solid #bbb',
                               center_background='#E7EDF5')
        top = frame.top.slotToolbar(slots='30,foo,*,my_buttons,50,boooo,15',height='20px')
        top.foo.div('Title...', font_size='1.2em')
        for i in ['info', 'key', 'keyboard', 'inbox', 'money', 'paper_plane', 'revert']:
            top.my_buttons.slotButton(i, iconClass='iconbox %s' %i, action="alert('%s action')" %i)
        for i in ['add_record', 'delete_record', 'lock']:
            top.boooo.slotButton(i, iconClass='iconbox %s' %i, action="alert('%s action')" %i)
        bottom = frame.bottom.slotToolbar(slots='30,btoh,*,goofy,30', height='30px')
        for i in range(1,11):
            bottom.btoh.slotButton(label=i, action='alert("Action of button n.%s")' %i)
        bottom.goofy.dateTextbox(width='14em')
        left = frame.left.slotToolbar('*,pr,*', height='342px')
        left.pr.slotButton('!!Prev',iconClass="iconbox previous", action='alert("Passing to the previous one...")')
        right = frame.right.slotToolbar('*,nxt,*', height='342px')
        right.nxt.slotButton('!!Next',iconClass="iconbox next", action='alert("Passing to the next one...")')
        frame.div('This is the center', margin='20px')
        
    def test_2_toolbars(self, pane):
        """slotBar, slotToolbar and CSS3"""
        pane.data('.color','black')
        pane.data('.from','#C4BFBD')
        pane.data('.to','#D6D1CE')
        pane = pane.framePane(frameCode='test2',height='350px',width='700px',
                              shadow='3px 3px 5px gray',rounded=10,
                              border='1px solid #bbb',margin='10px',
                              center_background='#E1E9E9')
        top = pane.top.slotToolbar(slots='10,hello,*,foo,*,searchOn',
                                   height='25px',gradient_from='^.from',gradient_to='^.to')
        view = pane.includedView(_newGrid=True)
        struct = view.gridStruct('name')
        view.selectionStore(table='showcase.person',order_by='$name',
                            _onStart=True,storeCode='mystore')
        top.hello.div(str(self.workdate),color='^.color')
        top.foo.div('Schedule',font_size='14pt',color='^.color')
        
        left = pane.left.slotToolbar(slotbarCode='left',slots='10,foo,*',width='40px',
                                     gradient_from='^.from',gradient_to='^.to')
        for i in ['star', 'save', 'print']:
            left.foo.slotButton(i, iconClass='iconbox %s' %i, action="alert('%s')" %i)
        
        right = pane.right.slotBar(slotbarCode='right',slots='20,dummy,*',width='130px',
                                   gradient_from='^.from',gradient_to='^.to',gradient_deg='^.deg')
        fb = right.dummy.formbuilder(lbl_color='^.color',cols=2)
        fb.div('Settings',font_size='12pt',color='^.color',colspan=2)
        fb.comboBox(lbl='color',value='^.color',width='90px',colspan=2,
                    values="""aqua,black,blue,fuchsia,gray,green,lime,maroon,
                              navy,olive,purple,red,silver,teal,white,yellow
                              """) # A complete list of CSS 3 basic color keywords
        fb.filteringSelect(lbl='from',value='^.from',width='90px',colspan=2,
                           values="""#8CBAD5:Blue,#FEFE87:Yellow,
                                     #E3AA00:Orange,#C4BFBD:Gray,
                                     #FB4343:Red""")
        fb.filteringSelect(lbl='to',value='^.to',width='90px',colspan=2,
                           values="""#9FE5F8:light Blue,#FFFED7:light Yellow,
                                     #F4DC7F:light Orange,#D6D1CE:light Gray,
                                     #FE6E61:light Red""")
        fb.verticalSlider(value='^.deg',minimum=0,maximum=360,discreteValues=361,
                          intermediateChanges=True,height='100px',lbl='Deg')
        fb.numbertextbox(value='^.deg',lbl='deg',width='3em')
        
        bottom = pane.bottom.slotToolbar(slots='300,bar,*',height='20px',
                                         gradient_from='^.from',gradient_to='^.to')
        bottom.bar.div('Here goes the messages for user',color='^.color')
        