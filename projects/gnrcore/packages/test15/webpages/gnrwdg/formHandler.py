# -*- coding: UTF-8 -*-

# formHandler.py
# Created by Francesco Porcari on 2011-01-12.
# Copyright (c) 2011 Softwell. All rights reserved.

"""Form Handler test"""

from gnr.web.gnrwebstruct import struct_method

class GnrCustomWebPage(object):
    dojo_source=True
    py_requires="gnrcomponents/testhandler:TestHandlerFull,gnrcomponents/formhandler:FormHandler,foundation/includedview:IncludedView"
    user_polling=0
    auto_polling=0
    
    @struct_method
    def formTester(self,pane,frameCode=None,startKey=None,**kwargs):
        form = pane.frameForm(frameCode=frameCode,table='glbl.provincia',
                              store='recordCluster',store_startKey=startKey or '*norecord*',**kwargs)
        form.testToolbar(startKey=startKey) 
        pane = form.center.contentPane(datapath='.record')
        fb = pane.formbuilder(cols=2, border_spacing='4px',fld_width="100%")
        fb.formContent()
        return form
        
    @struct_method
    def testToolbar(self,form,startKey=None):
        left = 'selector,|,' if not startKey else ''
        tb = form.top.slotToolbar('%s *,|,semaphore,|,formcommands,|,locker' %left,border_bottom='1px solid silver')
        if not startKey:
            fb = tb.selector.formbuilder(cols=1, border_spacing='1px')
            fb.dbselect(value="^.prov",dbtable="glbl.provincia",parentForm=False,#default_value='MI',
                                        validate_onAccept="if(userChange){this.form.publish('load',{destPkey:value})};",
                                        lbl='Provincia')
        return tb
        
    @struct_method
    def formContent(self,fb):
        fb.field('sigla',validate_len='2:2',validate_len_error="""Wrong lenght! (the field accept
                                                                  only a string of 2 characters)""")
                  #NISO: attenzione! la "validate_len" accetta solo:
                  #          validate_len_error='stringa'
                  #          validate_len_warning='stringa'
                  #
                  #      quindi non accetta i validate che c'erano prima, cioè:
                  #          validate_len_min_error='Too short',
                  #          validate_len_max_error='Too long')
        fb.field('regione')
        fb.field('nome',keepable=True)
        fb.field('codice_istat',keepable=True,validate_len='6:10')
        fb.field('ordine')
        fb.field('ordine_tot')
        fb.field('cap_valido')
        fb.checkbox(value='^.piero',keepable=True,label='Piero')
        return fb
        
    def onLoading_glbl_provincia(self,record,newrecord,loadingParameters,recInfo):
        if record['sigla'] == 'AO':
            recInfo['_readonly'] = True
            
    def test_0_frameform(self,pane):
        "Test FrameForm"
        form = pane.frameForm(frameCode='provincia_1',border='1px solid silver',datapath='.form',
                              rounded_bottom=10,height='180px',width='600px',pkeyPath='.prov')
        form.testToolbar()
        store = form.formStore(table='glbl.provincia',storeType='Item',handler='recordCluster',startKey='*norecord*',onSaved='reload')
        rpc = store.handler('load',default_ordine_tot='100')  
        rpc.addCallback('console.log(result)')  
        pane = form.center.contentPane(datapath='.record')
        fb = pane.formbuilder(cols=2).formContent()  
        
    def test_10_frameform_iv(self,pane):
        "Test FrameForm"
        form = pane.frameForm(frameCode='regione_b',border='1px solid silver',datapath='.form',
                            rounded_bottom=10,height='180px',width='600px',pkeyPath='.prov')
        form.testToolbar()
        store = form.formStore(table='glbl.provincia',storeType='Item',handler='recordCluster',startKey='*norecord*',onSaved='reload')
        store.handler('load',_onCalling='console.log("xxxx")',default_ordine_tot='100')    
        tc = form.center.tabContainer(datapath='.record')
        tc.contentPane(title='Provincia').formbuilder(cols=2, border_spacing='3px').formContent()
        bc =tc.borderContainer(title='Comuni')
        self.includedViewBox(bc,label='Comuni',datapath='comuni',
                             nodeId='comuni',table='glbl.localita',
                             struct='min',
                             reloader='^#regione_b_form.record.id', 
                             selectionPars=dict(where='$provincia=:provincia_id',
                             provincia_id='^#regione_b_form.record.sigla'))    
                             
    def test_2_formPane_dbl_cp(self,pane):
        bc = pane.borderContainer(height='180px')
        bc.formTester(frameCode='form_a',region='left',datapath='.pane1',width='50%',border='1px solid gray',margin_right='5px')
        bc.formTester(frameCode='form_b',region='center',datapath='.pane2',border='1px solid gray')
        
    def test_22_formPane_tc(self,pane):
        """First test description"""
        bc = pane.borderContainer(height='300px')
        topbc = bc.borderContainer(height='250px',region='top',splitter=True)
        bc.contentPane(region='center')
        tc = topbc.tabContainer(region='left',splitter=True,width='600px',nodeId='mytc')
        topbc.contentPane(region='center').div('pippo')
        t1 = tc.contentPane(title='Dummy',background_color='red')
        tc.formTester('form_tc',region='center',title='My Form',_lazyBuild=True)
        tc.contentPane(title='Third one')
        
    def test_3_formPane_palette(self,pane):
        pane = pane.div(height='30px')
        pane.dock(id='test_3_dock')
        pane.palette(paletteCode='province_lazy',title='Province',dockTo='test_3_dock',
                    _lazyBuild=True,_onLazyBuilt='console.log("aaa")').formTester('form_palette',height='300px',width='400px')
                    
    def test_8_formPane_tooltipForm(self,pane):
        box = pane.div(height='30px',width='100px',background='red',provincia='MI')
        box.span('Milano')
        dlg = box.tooltipPane(title='Milano',modifiers='shift',xconnect_onOpening='console.log(arguments);genro.formById("form_ttdialog").load({destPkey:e.target.sourceNode.attr.provincia});')
        dlg.formTester('form_ttdialog',height='300px',width='500px',background='white',rounded=6)
        
    def test_5_formPane_palette_remote(self,pane):
        fb = pane.formbuilder(cols=4, border_spacing='2px')
        fb.dbselect(value="^.provincia",dbtable="glbl.provincia")
        fb.button('open',action="""var paletteCode='prov_'+pkey;
        
                                   var palette = genro.src.create('palette',{paletteCode:paletteCode,title:'Palette:'+pkey,
                                                                               remote:'testPalette',remote_pkey:pkey,
                                                                               dockTo:false},
                                                                    paletteCode);
                                    """,
                    pkey='=.provincia')
    
        
    def remote_testPalette(self,pane,pkey=None,**kwargs):
        form = pane.formTester('formRemote_%s' %pkey,startKey=pkey,width='500px',height='300px')
            
    def test_4_formPane_dialog(self,pane):
        pane.button('Show dialog',action='genro.wdgById("province_dlg").show()')
        dialog = pane.dialog(title='Province',nodeId='province_dlg',closable=True).contentPane(_lazyBuild=True)
        dialog.formTester('form_dialog',height='300px',width='500px')
        
    @struct_method('mytoolbar_selectrecord')
    def mytoolbar_selectrecord(self,pane,**kwargs):
        fb=pane.formbuilder(cols=1, border_spacing='1px')
        fb.dbselect(value="^.prov",dbtable="glbl.provincia",parentForm=False,
                    validate_onAccept="this.form.publish('load',{destPkey:value});",lbl='Provincia')
                    
    def rpc_salvaDati(self, dati, **kwargs):
        print "Dati salvati:"
        print dati
        
    def test_111_frame_formdatapath(self,pane):
        form = pane.frameForm(frameCode='regione_a',border='1px solid silver',datapath='.form',
                            rounded_bottom=10,height='180px',width='600px',
                            pkeyPath='.prov')
        form.formStore(table='glbl.provincia',storeType='Item',
                      handler='recordCluster',startKey='MI',onSaved='reload')
        form.testToolbar()
        tc = form.center.tabContainer()
        pane =tc.contentPane(title='profile',datapath='.record')
        fb = pane.formbuilder(cols=1, border_spacing='2px')
        fb.field('sigla', validate_len='2:2',validate_len_min_error='Too Short')
        fb.field('regione')
        fb.field('nome')
        fb.field('codice_istat')
        fb.field('ordine')
        fb.field('ordine_tot')
        fb.field('cap_valido')
        slot_viewer = tc.contentPane(title='view',datapath='.viewer')
       #store = form.formStore(storepath='.record',table='glbl.provincia',storeType='Item',
       #                       handler='recordCluster',startKey='MI',onSaved='reload')
       #form.center.div('^.sigla')
        
        #fb = form.formbuilder(cols=1, border_spacing='2px')
        #fb.div('^.pippo')
        #fb.field('sigla', validate_len='2:2',validate_len_min_error='Too Short')
        #fb.field('regione')
        #fb.field('nome')
        #fb.field('codice_istat')
        #fb.field('ordine')
        #fb.field('ordine_tot')
        #fb.field('cap_valido')