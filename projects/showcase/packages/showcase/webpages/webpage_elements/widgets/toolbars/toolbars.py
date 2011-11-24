# -*- coding: UTF-8 -*-
"""Toolbars containers"""

from gnr.web.gnrwebstruct import struct_method

class GnrCustomWebPage(object):
    py_requires = """gnrcomponents/testhandler:TestHandlerFull"""
    
    def test_1_div(self, pane):
        """slotToolbar and toolBar attached on a div"""
        pane.div('You can attach a slotBar to any div:',
                  margin='0.5em', font_size='1.2em')
        top = pane.div().slotBar(slotbarCode='code',slots='hello,foo,dummy',
                                     gradient_from='#EED250',gradient_to='#F3DD8B',
                                     gradient_deg=-90)
        top.hello.div('Hello!')
        top.foo.div('MyTitle',font_size='14pt',color='^.color')
        top.dummy.button(label='add',iconClass='icnBaseAdd',action="alert('Added!')")
        
        pane.div('And you can attach a slotBar even to a contentPane:',
                  margin='0.5em', font_size='1.2em')
        cp = pane.contentPane().slotBar(slotbarCode='yeah2',height='40px',
                                        slots='*,hello',
                                        gradient_from='#ACACAC',gradient_to='#DEDEDE')
        cp.hello.slotButton('click me', iconClass='iconbox sum', action='alert("clicked!")')
        
    def test_2_features(self,pane):
        """framePane, slotToolbar and CSS 3"""
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
        
    def test_3_cb(self, pane):
        """Callback Slotbar"""
        pane = pane.slotToolbar(slots='0')
        pane.slotbar_form_navigation()
        
    @struct_method
    def sb_slotbar_form_navigation(self, pane, **kwargs):
        pane = pane.div(lbl='!!Navigation',_class='slotbar_group')
        pane.slotbar_form_dismiss()
        pane.slotbar_form_first()
        pane.slotbar_form_prev()
        pane.slotbar_form_next()
        pane.slotbar_form_last()
        
    @struct_method
    def sb_slotbar_form_dismiss(self, pane, caption=None, iconClass=None, **kwargs):
        pane.slotButton('!!Dismiss',iconClass="iconbox dismiss", action='alert("Dismissing...")')
        
    @struct_method          
    def sb_slotbar_form_first(self,pane,**kwargs):
        pane.slotButton('!!First',iconClass="iconbox first", action='alert("Passing to the first one...")')
    
    @struct_method          
    def sb_slotbar_form_prev(self,pane,**kwargs):
        pane.slotButton('!!Prev',iconClass="iconbox previous", action='alert("Passing to the previous one...")')
    
    @struct_method          
    def sb_slotbar_form_next(self,pane,**kwargs):
        pane.slotButton('!!Next',iconClass="iconbox next", action='alert("Passing to the next one...")')
        
    @struct_method          
    def sb_slotbar_form_last(self,pane,**kwargs):
        pane.slotButton('!!Last',iconClass="iconbox last", action='alert("Passing to the last one...")')