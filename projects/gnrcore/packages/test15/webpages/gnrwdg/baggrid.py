# -*- coding: UTF-8 -*-

# includedview_bagstore.py
# Created by Francesco Porcari on 2011-03-23.
# Copyright (c) 2011 Softwell. All rights reserved.

from gnr.core.gnrbag import Bag
from gnr.core.gnrdecorator import public_method

class GnrCustomWebPage(object):
    dojo_source = True
    css_requires='public'
    py_requires="gnrcomponents/testhandler:TestHandlerFull,gnrcomponents/framegrid:FrameGrid,th/th:TableHandler"
    
    def test_0_firsttest(self,pane):
        """First test description"""
        pane.data('.dati',self.getDati())
        pane.dataController('SET .gridstore = dati.deepCopy();',dati='=.dati',_fired='^loadBag')
        frame = pane.bagGrid(frameCode='test',title='Test',struct=self.gridstruct,height='300px',
                            table='glbl.localita',storepath='.gridstore',
                            default_provincia='MI',
                            default_qty=4)
        frame.bottom.button('Load',fire='.loadBag')
        
    def gridstruct(self, struct):
        r = struct.view().rows()
        r.fieldcell('provincia',edit=dict(selected_codice_istat='.cist'),
                    table='glbl.provincia',caption_field='provincia_nome')
        r.cell('qty',dtype='N',name='Quantitativo',width='5em',edit=True)  
        r.cell('colli',dtype='L',name='Colli',width='5em',edit=True)  
        r.cell('totale',dtype='L',name='Colli',width='5em',formula='colli*qty')  
        r.cell('cist',name='Codice istat')

    def test_1_remotestruct(self,pane):
        """First test description"""
        pane.data('.dati',self.getDati())
        pane.dataController('SET .xxx = dati.deepCopy();',dati='=.dati',_fired='^zzz')
        frame = pane.bagGrid(frameCode='test',title='Test',structpath='yyy',height='300px',
                            table='glbl.localita',storepath='.xxx',default_provincia='MI',default_qty=4)
        frame.bottom.button('Load',fire='zzz')

        frame.bottom.button('Load Struct',fire='kkk')
        pane.dataRpc('yyy',self.r_gridstruct,_fired='^kkk')

        #editor = frame.grid.gridEditor()
        #editor.dbSelect(gridcell='provincia',dbtable='glbl.provincia') #zzvalue='^.provincia_sigla'
    
    @public_method
    def r_gridstruct(self):
        struct = self.newGridStruct()
        r = struct.view().rows()
        r.fieldcell('provincia',edit=dict(selected_codice_istat='.cist'),table='glbl.provincia',caption_field='provincia_nome')
        r.cell('qty',dtype='L',name='Quantitativo',width='5em',edit=True)  
        r.cell('colli',dtype='L',name='Colli',width='5em',edit=True)  
        r.cell('totale',dtype='L',name='Colli',width='5em',formula='colli*qty')  
        r.cell('cist',name='Codice istat')
        return struct

    def getDati(self):
        result = Bag()
        result.setItem('r_0',Bag(dict(provincia = 'MI',qty=13,provincia_nome='Milano',cist='044')))
        result.setItem('r_1',Bag(dict(provincia = 'CO',qty=22,provincia_nome='Como',cist='039')))
        return result


    def test_2_rrc(self,pane):
        """First test description"""
        pane.data('.dati',self.getDati())
        pane.dataController('SET .gridstore = dati.deepCopy();',dati='=.dati',_fired='^loadBag')
        frame = pane.bagGrid(frameCode='rrc',title='remoteRowController test',struct=self.gridstruct_2,height='300px',
                            table='glbl.localita',storepath='.gridstore',
                            grid_remoteRowController=self.test_remoteRowController,
                            default_descrizione='riga acquisto',
                            grid_remoteRowController_defaults=dict(provincia='MI',qty=8),
                            grid_menuPath='aaa')
        b = Bag()
        b.setItem('m_1',None,caption='poppo',action='ciao')
        pane.data('aaa',b)
        bar = frame.bottom.slotBar('loadbtn,testbtn')
        bar.loadbtn.button('Load',fire='.loadBag')
        bar.testbtn.button('Test',action="""
            var t = new gnr.GnrBag();
            t.setItem('r2',null,{city:'roma',address:'corso como'});
            t.setBackRef();
            var v = t.getItem('r2.city?=#z')
            console.log('xxxx',v)
            """)

        
    def gridstruct_2(self, struct):
        r = struct.view().rows()
        r.fieldcell('provincia',edit=dict(remoteRowController=True),
                    table='glbl.provincia',caption_field='provincia_nome',width='18em')
        r.cell('colore',edit=True,name='Colore',width='10em')
        r.cell('qty',dtype='N',name='Qty',width='5em',edit=dict(remoteRowController=True))  
        r.cell('colli',dtype='L',name='Colli',width='5em',edit=dict(remoteRowController=True),
                disabled='=#ROW.qty?=#v<2')  
        r.cell('descrizione',name='Desc',width='10em',color='=#ROW.colore')  
        r.cell('totale',dtype='N',name='Tot',width='5em')  
        r.cell('cist',name='C. istat',width='7em')

    @public_method
    def test_remoteRowController(self,row=None,field=None,provincia=None,qty=None):
        if row['qty']:
            print row


    def test_5_menuPath(self,pane):
        """First test description"""
        pane.data('.dati',self.getDati())
        pane.dataController('SET .gridstore = dati.deepCopy();',dati='=.dati',_fired='^loadBag')
        pane.bagGrid(frameCode='mpath',title='Menupath test',struct=self.gridstruct_2,height='300px',
                            table='glbl.localita',storepath='.gridstore')

    def test_6_menuAppend(self,pane):
        """First test description"""
        pane.data('.dati',self.getDati())
        pane.dataController('SET .gridstore = dati.deepCopy();',dati='=.dati',_fired='^loadBag')
        frame = pane.bagGrid(frameCode='mappend',title='Menu append test',struct=self.gridstruct_2,height='300px',
                            table='glbl.localita',storepath='.gridstore')
        frame.grid.menu(storepath='bbb')
        b = Bag()
        b.setItem('m_1',None,caption='mario')
        pane.data('bbb',b)


    def test_7_picker(self,pane):
        pane.data('.mygrid.dati',self.getDati())
        frame = pane.bagGrid(frameCode='mpath',datapath='.mygrid',struct=self.gridstruct_2,height='300px',
                            table='glbl.localita',storepath='.dati')
        bar = frame.top.bar.replaceSlots('addrow','testpicker')
        bar.testpicker.palettePicker(grid=frame.grid,
                                    table='glbl.provincia',#paletteCode='mypicker',
                                    viewResource='View',
                                    checkbox=True,defaults='sigla,nome')


    def test_9_bagridformula(self,pane):
        def struct(struct):
            r = struct.view().rows()
            r.cell('description',name='Description',width='15em',edit=True)

            r.cell('number',name='Number',width='7em',dtype='L',edit=True,columnset='ent')
            r.cell('price',name='Price',width='7em',dtype='N',edit=True,columnset='ent')
            r.cell('total',name='Total',width='7em',dtype='N',formula='number*price',
                    totalize='.sum_total',format='###,###,###.00')
            r.cell('discount',name='Disc.%',width='7em',dtype='N',edit=True,columnset='disc')
            r.cell('discount_val',name='Discount',width='7em',dtype='N',formula='total*discount/100',
                    totalize='.sum_discount',columnset='disc')
            r.cell('net_price',name='F.Price',width='7em',dtype='N',
                        formula='total-discount_val',totalize='.sum_net_price',columnset='tot')
            r.cell('vat',name='Vat',width='7em',dtype='N',
                    formula='net_price+net_price*vat_p/100',formula_vat_p='^vat_perc',
                    totalize='.sum_vat',format='###,###,###.00',columnset='tot')
            r.cell('gross',name='Gross',width='7em',dtype='N',formula='net_price+vat',
                    totalize='.sum_gross',format='###,###,###.00',columnset='tot')
        bc = pane.borderContainer(height='400px',width='800px')
        top = bc.contentPane(region='top',height='40px')
        fb = top.formbuilder(cols=2,border_spacing='3px')
        bc.contentPane(region='right',splitter=True,width='5px')
        bc.contentPane(region='bottom',splitter=True,height='50px')
        fb.numberTextBox(value='^vat_perc',lbl='Vat perc.',default_value=10)
        fb.button('clear',fire='.clear')
        bc.dataFormula('.surfaces.store',"new gnr.GnrBag({r1:new gnr.GnrBag({description:'pipp'})})",_onStart=True,_fired='^.clear')
        frame = bc.contentPane(region='center').bagGrid(frameCode='formule',datapath='.surfaces',
                                                    struct=struct,height='300px',fillDown=True,
                                                    footer='Totals',
                                                    pbl_classes=True,margin='5px',
                                                    columnset_ent='Enterable',
                                                    columnset_disc='Discount',
                                                    columnset_tot='Totals',
                                                    columnset_tot_background='red'
                                                    )

        #f = frame.grid.footer()
#
        #f.item('description',colspan=3,value='Pippo',text_align='right')
       #f.item('total')
       #f.item('discount_val')
       #f.item('net_price')
       ##f = grid.footer()
       #
       #f.item('gross')
       #f.item('vat')



