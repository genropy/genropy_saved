# -*- coding: UTF-8 -*-

# slotbar.py
# Created by Francesco Porcari on 2011-01-30.
# Copyright (c) 2011 Softwell. All rights reserved.

"""slotbar"""

from gnr.web.gnrwebstruct import struct_method
from gnr.core.gnrbag import Bag
from gnr.core.gnrdecorator import public_method

class GnrCustomWebPage(object):

    py_requires="gnrcomponents/testhandler:TestHandlerFull,th/th:TableHandler"
    
    def windowTitle(self):
        return 'Multibutton test'
        
    

    def test_0_multibutton_base(self,pane):
        pane.multibutton(value='^.base',values='pippo:Pippo,paperino:Paperino')
        pane.textbox(value='^.base')



    def test_1_multibutton_item(self,pane):
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
        mb = pane.multibutton(value='^.base',sticky=False,)
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

    def test_36_multibutton_insert(self, pane):
        pane.data('.regioni.store', Bag())
        mbreg= pane.multibutton(value='^.regione', items='^.regioni.store',
                        identifier='sigla',caption='nome',deleteAction=True)
        mbreg.plusItem(ask=dict(title='Nuova regione',fields=[
                    dict(name='sigla',selected_nome='.nome',
                            lbl='Regione',wdg='dbselect',dbtable='glbl.regione')
                ]),selectLast=True)
       #mbreg.item(code='add_regione',caption='+',sticky=False,

       #            action="this.getParentNode().publish('appendItem',{nome:regione_nome,sigla:regione_sigla,deleteAction:true})",
       #        ask=dict(title='Nuova regione',fields=[
       #            dict(name='regione_sigla',selected_nome='.regione_nome',
       #                    lbl='Regione',wdg='dbselect',dbtable='glbl.regione')
       #        ]))
        

        mbprov = pane.multibutton(value='^.provincia_selected',caption='nome', deleteAction=True)
        mbprov.store(table='glbl.provincia',where='$regione=:reg',reg='^.regione')

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


