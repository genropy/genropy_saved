# -*- coding: utf-8 -*-

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
        pane.dataController('SET .gridstore = dati.deepCopy();',dati='=.dati',_fired='^.loadBag')
        pane.dataFormula('.gridstore',"new gnr.GnrBag();",_onStart=True)
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
        r.cell('totale',dtype='L',name='Tot',width='5em',formula='colli*qty')  
        r.cell('cist',name='Codice istat')
       # r.cell('montano',dtype='B',edit=True)

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
            r.cell('description',name='^first_header_name',width='15em',edit=True,hidden='^hidden_0')

            r.cell('number',name='Number',width='7em',dtype='L',hidden='^hidden_1',
                    edit=True,columnset='ent')
            r.cell('price',name='Price',width='7em',dtype='N',hidden='^hidden_2',
                    edit=True,columnset='ent')
            r.cell('total',name='Total',width='7em',dtype='N',formula='number*price',hidden='^hidden_3',
                    totalize='.sum_total',format='###,###,###.00')
            r.cell('discount',name='Disc.%',width='7em',dtype='N',edit=True,columnset='disc',hidden='^hidden_4')
            r.cell('discount_val',name='Discount',width='7em',dtype='N',formula='total*discount/100',
                    totalize='.sum_discount',hidden='^hidden_5',
                    columnset='disc')
            r.cell('net_price',name='F.Price',width='7em',dtype='N',
                        formula='total-discount_val',totalize='.sum_net_price',
                        columnset='tot',hidden='^hidden_6')
            r.cell('vat',name='Vat',width='7em',dtype='N',
                    formula='net_price+net_price*vat_p/100',formula_vat_p='^vat_perc',
                    totalize='.sum_vat',format='###,###,###.00',columnset='tot',hidden='^hidden_7')
            r.cell('gross',name='Gross',width='7em',dtype='N',formula='net_price+vat',
                    totalize='.sum_gross',format='###,###,###.00',columnset='tot',hidden='^hidden_8')

        bc = pane.borderContainer(height='400px',width='800px')
        top = bc.contentPane(region='top',height='80px')
        fb = top.formbuilder(cols=10,border_spacing='3px')
        bc.contentPane(region='right',splitter=True,width='5px')
        bc.contentPane(region='bottom',splitter=True,height='50px')
        fb.numberTextBox(value='^vat_perc',lbl='Vat perc.',default_value=10,colspan='10')
        fb.data('first_header_name','Variable head')
        fb.textbox(value='^first_header_name',lbl='First header')
        fb.textbox(value='^colsetname',lbl='Colset',default_value='Enterable')
        fb.textbox(value='^colsetentbg',lbl='Colset bg',default_value='green')

        fb.br()
        for i in range(9):
            fb.checkbox(value='^hidden_%s' %i,label='last %s' %i)

        fb.button('clear',fire='.clear')
        bc.dataFormula('.surfaces.store',"new gnr.GnrBag({r1:new gnr.GnrBag({description:'pipp'})})",_onStart=True,_fired='^.clear')
        frame = bc.contentPane(region='center').bagGrid(frameCode='formule',datapath='.surfaces',
                                                    struct=struct,height='300px',fillDown=True,
                                                    grid_footer='Totals',
                                                    pbl_classes=True,margin='5px',
                                                    columnset_ent='^colsetname',
                                                    columnset_disc='Discount',
                                                    columnset_tot='Totals',
                                                    columnset_ent_background='^colsetentbg',
                                                    columnset_tot_background='red'
                                                    )

       # f = frame.grid.footer()
       # f.item('description',value='Questa fattura ha valore',colspan=3,text_align='center')
       # f = frame.grid.footer()
       # f.item('description',value='test',colspan=2,text_align='center')

       #f.item('total')
       #f.item('discount_val')
       #f.item('net_price')
       ##f = grid.footer()
       #
       #f.item('gross')
       #f.item('vat')

    def test_10_autorow(self,pane):
        bc = pane.borderContainer(height='400px')
        fb = bc.contentPane(region='top').formbuilder(cols=2,border_spacing='3px')
        fb.checkbox(value='^autoInsert',label='autoInsert',default=True)
        fb.checkbox(value='^autoDelete',label='autoDelete',default=True)

        fb.textbox(value='^.pippo',lbl='Pippo')
        fb.textbox(value='^.pluto',lbl='Pluto')

        bc.bagGrid(frameCode='test_10',title='AutoInsert',datapath='.mygrid',
                            struct=self.gridstruct,region='center',
                            storepath='.data',
                            addrow='auto',delrow='auto',
                            default_colli=4)

        fb = bc.contentPane(region='bottom').formbuilder(cols=2,border_spacing='3px')
        fb.textbox(value='^.foo',lbl='foo')
        fb.textbox(value='^.bar',lbl='bar')


    def test_11_multi(self,pane):
        bc = pane.borderContainer(height='800px')
        top = bc.contentPane(region='top',height='200px',splitter=True,background='lime')
        innerbc = bc
        l = ['alfa','beta','gamma','pippo']
        s = len(l)
        for r in l:
            region,height=('center',None) if s==1 else ('top','%s%%' %(100./s))
            innerbc = innerbc.borderContainer(region='center')
            innerbc.bagGrid(frameCode=r ,title=r,datapath='.%s' %r,region=region,splitter=True,
                        struct=self.gridstruct,height=height,
                        addrow='auto',delrow='auto')
            s-=1


    def test_13_autorow_date(self,pane):
        bc = pane.borderContainer(height='300px')
        top = bc.contentPane(region='top')
        fb = top.formbuilder(cols=1,border_spacing='3px')
        fb.dateTextBox(value='^s_date_base',lbl='Start date')
        fb.dataController("""
            sd = sd || new Date();
            var y = sd.getFullYear();
            var m = sd.getMonth();
            for (var i=1;i<32; i++){
                d = new Date(y,m,i);
                if(d.getMonth()!=m){
                    d = null;  
                }
                genro.setData('s_date_'+i,d);
            }

            """, sd='^s_date_base',_init=True)

        center = bc.contentPane(region='center')

        def struct(struct):
            r = struct.view().rows()
            r.cell('name',description='Name',width='15em',edit=True)
            for i in range(1,32):
                r.cell('day_%02i' %i, name='^s_date_%i' %i,name_format='EEE d',
                    hidden='^s_date_%i?=!#v' %i,dtype='N',edit=True)

        center.bagGrid(storepath='.store',title='Date grid',struct=struct,datapath='.mygrid',
                    addrow='auto',delrow='auto')

    def test_20_structinfo(self,pane):

        def struct(struct):
            r = struct.view().rows()
            r.cell('description',name='Description',width='15em',edit=True)
            
            cs_ent = r.columnset('ent',name='Enterable',background='red',color='white',
                                cells_background='RGBA(194, 37, 49, 0.05)',
                                cells_width='7em',cells_edit=True)

            cs_ent.cell('number',name='Number',dtype='L')
            cs_ent.cell('price',name='Price',dtype='N')

            r.cell('total',name='Total',width='7em',dtype='N',formula='number*price',
                    totalize='.sum_total',format='###,###,###.00')

            cs_disc = r.columnset('disc',name='^.discountName',background='^.discountBG')

            cs_disc.cell('discount',name='Disc.%',width='7em',dtype='N',edit=True)
            cs_disc.cell('discount_val',name='Discount',width='7em',dtype='N',formula='total*discount/100',
                    totalize='.sum_discount')

            cs_tot = r.columnset('tot',name='Totals',background='RGBA(255, 253, 123, 1.00)',
                        cells_background='RGBA(255, 253, 123, 0.10)',color='#666')

            cs_tot.cell('net_price',name='F.Price',width='7em',dtype='N',
                        formula='total-discount_val',totalize='.sum_net_price',
                        columnset='tot')
            cs_tot.cell('vat',name='Vat',width='7em',dtype='N',
                    formula='net_price+net_price*vat_p/100',formula_vat_p='^vat_perc',
                    totalize='.sum_vat',format='###,###,###.00',columnset='tot')
            cs_tot.cell('gross',name='Gross',width='7em',dtype='N',formula='net_price+vat',
                    totalize='.sum_gross',format='###,###,###.00',columnset='tot')

    
        bc = pane.borderContainer(height='400px',width='800px')
        fb = bc.contentPane(region='top').formbuilder()
        fb.textbox(value='^.mygrid.grid.discountName',lbl='Name')
        bc.data('.mygrid.grid.discountName','Discount')
        fb.textbox(value='^.mygrid.grid.discountBG',lbl='Background')
        bc.data('.mygrid.grid.discountBG','green')
        fb.textbox(value='^.mygrid.grid.struct.info.columnsets.disc?cells_background',lbl='Cells BG')
        bc.data('.mygrid.grid.struct.info.columnsets.disc?cells_background','')


        frame = bc.contentPane(region='center').bagGrid(frameCode='structinfo',datapath='.mygrid',
                                                    struct=struct,height='300px',
                                                    grid_configurable=True,
                                                    pbl_classes=True,margin='5px')

    def test_99_mixedmode(self,pane):
        frame = pane.bagGrid(frameCode='V_trasporti',struct=self.gridstruct,table='glbl.localita',
                            storepath='.gridstore',height='400px')
        form = frame.grid.linkedForm(frameCode='F_trasporti',
                                 datapath='.form',loadEvent='onRowDblClick',
                                 dialog_height='200px',dialog_width='350px',
                                 dialog_title='Edit',handlerType='dialog',
                                 childname='form',attachTo=pane,
                                 store='memory',default_qty=1,
                                 #store_pkeyField='code'
                                 )
        pane.data('.dati',self.getDati())
        pane.dataController('SET .gridstore = dati.deepCopy();',dati='=.dati',_fired='^.loadBag')
        frame.bottom.button('Load',fire='.loadBag')
        self.miaForm(form)
    
    def miaForm(self,form):
        fb = form.record.formbuilder()
        fb.dbSelect(value='^.provincia',selected_codice_istat='.cist',
                        dbtable='glbl.provincia',lbl='Provincia',
                        selected_nome='.provincia_nome')
        #r.fieldcell('provincia',edit=dict(selected_codice_istat='.cist'),
        #            table='glbl.provincia',caption_field='provincia_nome')
        fb.numberTextBox(value='^.qty',lbl='Qty')
        fb.numberTextBox(value='^.colli',lbl='Colli')
        bar = form.bottom.slotToolbar('*,cancelbtn,savebtn,5',height='20px')
        bar.cancelbtn.slotButton('Cancello',action="this.form.abort()")
        bar.savebtn.slotButton('Salva',action="this.form.save({destPkey:'*dismiss*'})")

        #r.cell('totale',dtype='L',name='Colli',width='5em',formula='colli*qty')  
        #r.cell('cist',name='Codice istat')