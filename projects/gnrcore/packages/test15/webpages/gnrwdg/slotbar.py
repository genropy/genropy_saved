# -*- coding: utf-8 -*-

# slotbar.py
# Created by Francesco Porcari on 2011-01-30.
# Copyright (c) 2011 Softwell. All rights reserved.

"""slotbar"""

from builtins import object
from gnr.web.gnrwebstruct import struct_method
from gnr.core.gnrbag import Bag
from gnr.core.gnrdecorator import public_method

class GnrCustomWebPage(object):
    testOnly = '_0_'
    py_requires="gnrcomponents/testhandler:TestHandlerFull,th/th:TableHandler"
    
    def windowTitle(self):
        return 'SlotBar test'
        
    def test_0_slotbar_base(self,pane):
        """Basic slotbar"""
        frame = pane.framePane(frameCode='frameOne',height='100px',shadow='3px 3px 5px gray',
                                border='1px solid #bbb',rounded_top=10,margin='10px')
        top = frame.top.slotBar(slots='30,foo,|,Antonio,*,|,bar',height='20px')
        top.foo.div('foo',width='100px',background='navy',lbl='Foo')
        top.bar.myslot()
        
    def test_1_slotbar(self,pane):
        """CSS on slotbar"""
        frame = pane.framePane(frameCode='frameOne',height='100px',shadow='3px 3px 5px gray',
                                border='1px solid #bbb',rounded_top=10,margin='10px')
        top = frame.top.slotBar(slots='*,|,foo,bar,|,*',
                                gradient_deg=90,gradient_from='#fff',gradient_to='#bbb',
                                border_bottom='1px solid #bbb',rounded_top=10,lbl_position='T',lbl_color='red',
                                lbl_font_size='7px')
        top.foo.div('foo',width='100px',background='navy',lbl='Foo')
        top.bar.myslot()
        
    def test_2_slotToolbar(self,pane):
        """CSS on slotToolbar"""
        frame = pane.framePane(frameCode='frameTwo',height='100px',shadow='3px 3px 5px gray',
                                border='1px solid #bbb',rounded_top=10,margin='10px')
        top = frame.top.slotToolbar(slots='*,|,foo,bar,|,*,xx',
                                    gradient_deg='90',gradient_from='#fff',gradient_to='#bbb',
                                    border_bottom='1px solid #bbb',rounded_top=10,
                                    lbl_position='T',lbl_color='red',lbl_font_size='7px')
        top.foo.div('foo',width='100px',color='white',background='teal',lbl='labelFoo')
        top.bar.myslot()
        top.xx.div(width='1px')
        
    def test_3_slotToolbar_vertical(self,pane):
        """slotToolbar vertical"""
        frame = pane.framePane(frameCode='frameTwo',height='300px',shadow='3px 3px 5px gray',
                                border='1px solid #bbb',rounded_left=10,margin='10px')
        sl = frame.left.slotToolbar(slots='10,foo,*,|,bar,|,*,spam,*',
                                    border_right='1px solid gray',
                                    gradient_from='#bbb',gradient_to='#fff',
                                    rounded_left=10,toolbar=True)
        sl.foo.button(label='Add',iconClass='icnBaseAdd',showLabel=False)
        sl.bar.button(label='Del',iconClass='icnBaseOk',showLabel=False)
        sl.spam.div(height='18px',width='16px',background='blue')

    def test_4_slotToolbar_replaceslots(self,pane):
        """slotToolbar vertical"""
        frame = pane.framePane(height='100px',shadow='3px 3px 5px gray',
                                border='1px solid #bbb',rounded_top=10,margin='10px')
        bar = frame.top.slotBar('aaa,bbb',aaa='Piero',bbb='Pippo')
        bar.replaceSlots('bbb','ccc',ccc='Pancrazio')
        
    @struct_method
    def myslot(self,pane):
        pane.button(label='Bar',iconClass='icnBaseAdd',showLabel=False,lbl='hello')

    def test_5_slotToolbar_multiline(self,pane):
        """Multiline"""
        frame = pane.framePane(frameCode='frameMultiline',height='100px',shadow='3px 3px 5px gray',
                                border='1px solid #bbb',rounded_top=10,margin='10px')

        upperbar = frame.top.slotToolbar(slots='*,xxx,*',
                                    gradient_deg='90',gradient_from='#fff',gradient_to='lime',
                                    border_bottom='1px solid #bbb',
                                    lbl_position='T',lbl_color='red',lbl_font_size='7px',childname='topupper')
        upperbar.xxx.multibutton(values='^.multibutton_values',value='^.abx',multivalue=True,mandatory=False)
        upperbar.dataController('SET .multibutton_values = v',v ='^.valuesetter')

        top = frame.top.slotToolbar(slots='*,|,foo,bar,|,*,xx',
                                    gradient_deg='90',gradient_from='#fff',gradient_to='#bbb',
                                    border_bottom='1px solid #bbb',splitter=True,
                                    lbl_position='T',lbl_color='red',lbl_font_size='7px')


        top.foo.div('foo',width='100px',color='white',background='teal',lbl='labelFoo')
        top.bar.myslot()
        top.xx.div(width='1px')     
        frame.textbox(value='^.valuesetter')
        frame.dataFormula('.valuesetter','v',v = 'pippo:mmaa:Pippo,pluto:Pluto,paperino:Paperino',_onStart=True)


        center = frame.center.contentPane()
        center.textbox(value='^.abx')



    def test_7_slotToolbar_multibutton_base(self,pane):
        pane.multibutton(value='^.base',values='pippo:Pippo,paperino:Paperino')
        pane.textbox(value='^.base')



    def test_11_slotToolbar_multibutton_base(self,pane):
        pane.dataController("console.log(z);",z='^.base')
        mb = pane.multibutton(value='^.base',sticky=False)

        mb.item('pippo',caption='Pippo')
        mb.item('paperino',caption='Paperino')
        mb.item('delayed',caption='Delayed',_delay=400)
        mb.item('different',caption='Different',action='alert("I am different")')


    def test_8_slotToolbar_multibutton_items_path(self,pane):
        pane.data('.multibutton.data',self.getmbdata())
        pane.multibutton(value='^.base',items='^.multibutton.data')
        pane.textbox(value='^.base')


    def test_10_slotToolbar_multibutton_items_struct(self,pane):
        pane.checkbox(value='^.disabled')
        mb = pane.multibutton(value='^.base',sticky=False)
        mb.item('pippo',caption='Pippo',disabled='^.disabled',action='alert("xxx")')
        mb.item('paperino',caption='Paperino',deleteAction='genro.bp(true)')

    def test_6_slotToolbar_multibutton_storepath(self,pane):
        """Multiline"""
        frame = pane.framePane(frameCode='frameMultiline',height='100px',shadow='3px 3px 5px gray',
                                border='1px solid #bbb',rounded_top=10,margin='10px')
        bar = frame.top.slotToolbar(slots='*,mb,*')

        bar.data('.multibutton.data',self.getmbdata())
        bar.mb.multibutton(value='^.multibutton.value',storepath='.multibutton.data')
        frame.textbox(value='^.multibutton.value')
        frame.textbox(value='^.multibutton.data.pippo?caption')

    def getmbdata(self):
        result = Bag()
        result.setItem('pippo',None,caption='Pippo')
        result.setItem('pluto',None,caption='Pluto')
        result.setItem('paperino',None,caption='Paperino')
        return result


    def test_12_slotToolbar_multibutton_store(self,pane):
        frame = pane.framePane(frameCode='frameMultibuttonStore',height='400px')
        bar = frame.top.slotToolbar(slots='10,selettore_regione,*,mb,10')
        bar.selettore_regione.dbselect(value='^.regione',dbtable='glbl.regione')
        mb = bar.mb.multibutton(value='^.provincia_selected',caption='nome')
        mb.store(table='glbl.provincia',where='$regione=:reg',reg='^.regione')


    def test_13_multibuttonForm(self,pane):
        bc = pane.borderContainer(height='500px')
        fb = bc.contentPane(region='top').formbuilder(cols=1,border_spacing='3px')
        fb.button('Remoto',action='genro.dlg.remoteDialog("pr_multi","multibuttonRegione");')
        fb.dbselect(value='^aux.regione',dbtable='glbl.regione',lbl='Regione')



    def test_14_slotToolbar_multibutton_store(self,pane):
        frame = pane.framePane(frameCode='frameMultibuttonStore',height='400px')
        bar = frame.top.slotToolbar(slots='10,selettore_regione,*,mb_0,5,mb,5,mb_1,10')
        bar.selettore_regione.dbselect(value='^.regione',dbtable='glbl.regione')
        mb_0 = bar.mb_0.multibutton(value='^.curval',caption='nome',mandatory=False)
        mb_0.item('Pippo',sticky=True)
        #mb_0.item('Pluto',sticky=True)

        mb = bar.mb.multibutton(value='^.curval',caption='nome',mandatory=False)
        mb.store(table='glbl.provincia',where='$regione=:reg',reg='^.regione')


        mb_1 = bar.mb_1.multibutton(value='^.curval',caption='nome',hidden='^.regione?=#v!="LAZ"',mandatory=False)
        mb_1.item('Paperino',sticky=True)
        #mb_1.item('Pancrazio',sticky=True)


    @public_method
    def multibuttonRegione(self,pane,**kwargs):
        bc = pane.borderContainer(height='300px',width='400px',datapath='pippo') #.div('bao')
        bc.contentPane(region='center').multiButtonForm(table='glbl.provincia',condition='$regione=:reg',
                                condition_reg='^aux.regione',condition__onBuilt=True,formResource='Form')



   #def test_14_multibuttonForm(self,pane):
   #    pane.multiButtonForm(table='glbl.provincia',condition='$regione=:reg',reg='MOL',switch='zona',
   #                        form_nord=dict(table='glbl.provincia',formResource='Alfa'),
   #                        form_sud=dict(table='glbl.provincia',formResource='Beta'),
   #                        form_centro=dict(table='glbl.pippo',keyfield='zzz'))

   #    


