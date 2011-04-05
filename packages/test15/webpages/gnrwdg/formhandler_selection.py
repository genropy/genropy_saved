# -*- coding: UTF-8 -*-

# formhandler_selection.py
# Created by Francesco Porcari on 2011-01-18.
# Copyright (c) 2011 Softwell. All rights reserved.

from gnr.web.gnrwebstruct import struct_method
from gnr.web.gnrwebpage import rpc_method
"Test formhandler selection store"
class GnrCustomWebPage(object):
    testOnly='_2_'
    user_polling=0
    auto_polling=0
    py_requires="""gnrcomponents/testhandler:TestHandlerFull,
                    gnrcomponents/formhandler:FormHandler,
                    gnrcomponents/selectionhandler:SelectionHandler"""
    
    @struct_method
    def formTester(self,pane,frameCode=None,startKey=None,**kwargs):                
        form = pane.frameForm(frameCode=frameCode,rounded_bottom=10,**kwargs)
        form.testToolbar()
        store = form.formStore(storepath='.record',table='glbl.provincia',storeType='Collection',
                               handler='recordCluster')  
        fb = form.formbuilder(cols=2, border_spacing='4px', width="400px",fld_width="100%")
        fb.formContent()
        return form
        
    @struct_method
    def testToolbar(self,form,startKey=None):
        left = 'selectrecord,|,' if not startKey else ''
        tb = form.top.slotToolbar('navigation,*,|,semaphore,|,formcommands,|,locker',border_bottom='1px solid silver')
        return tb
        
    @struct_method
    def formContent(self,fb):
        fb.field('sigla',validate_nodup=True)
        fb.field('regione')
        fb.field('nome')
        fb.field('codice_istat')
        fb.field('ordine')
        fb.field('ordine_tot')
        fb.field('cap_valido')
        return fb
         
    def test_0_base(self,pane):
        bc = pane.borderContainer(height='250px')
        frame = bc.framePane('province',region='left',width='300px')
        
        tb = frame.top.slotToolbar('*,selector,20,reloader')
        tb.selector.dbselect(value='^.regione',dbtable='glbl.regione',lbl='Regione')
        tb.reloader.button('reload',fire='.reload')
        iv = frame.includedView(struct='regione',autoSelect=True,selectedId='.selectedPkey',
                           selfsubscribe_onSelectedRow='genro.formById("provincia_form").publish("load",{destPkey:$1.selectedId});',
                           subscribe_form_provincia_onLoaded="this.widget.selectByRowAttr('_pkey',$1.pkey)")
        iv.selectionStore(table='glbl.provincia',where='$regione=:r',r='^.regione',_fired='^.reload')
                          
        center = bc.contentPane(region='center',border='1px solid blue').formTester(frameCode='provincia')
    
        
    def test_1_base(self,pane):
        bc = pane.borderContainer(height='250px')
        frame = bc.framePane('province',region='left',width='600px')
        
        tb = frame.top.slotToolbar('selector,searchOn,reloader,count')
        tb.selector.dbselect(value='^.regione',dbtable='glbl.regione',lbl='Regione')
        tb.reloader.button('reload',fire='.reload')
        iv = frame.includedView(struct='regione',autoSelect=True,selectedId='.selectedPkey',
                           selfsubscribe_onSelectedRow='genro.formById("provincia_form").publish("load",{destPkey:$1.selectedId});',
                           subscribe_form_provincia_onLoaded="this.widget.selectByRowAttr('_pkey',$1.pkey)")
        iv.selectionStore(table='glbl.provincia',where='$regione=:r',r='^.regione',_fired='^.reload')
                          
        center = bc.contentPane(region='center').formTester(frameCode='provincia')
        center.dataRpc('test',self.test, _onStart=True)
        
    @public_method
    def test(self):
        return 'Funzio'
    
    def test_2_linkedForm(self,pane):
        bc = pane.borderContainer(height='250px')
        frame = bc.framePane('province',region='left',width='300px')
        tb = frame.top.slotToolbar('selector,*,iv_add,10')
        tb.selector.dbselect(value='^.regione',dbtable='glbl.regione',lbl='Regione')
        iv = frame.includedView(struct='regione',autoSelect=True)
        iv.selectionStore(table='glbl.provincia',where='$regione=:r',
                          r='^.regione',_fired='^.reload')
        center = bc.contentPane(region='center',border='1px solid blue')
        form = iv.linkedForm(frameCode='provincia',loadEvent='onRowDblClick',
                            dialog_title='Prova',
                            dialog_height='300px',
                            dialog_width='400px')
        form.store.handler('load',default_regione='=#province_frame.regione')
        form.testToolbar()
        saver = form.store.handler('save')        
        fb = form.formbuilder(cols=2, border_spacing='4px', width="400px",fld_width="100%").formContent()
    
    def test_3_linkedForm_pane(self,pane):
        bc = pane.borderContainer(height='250px')
        frame = bc.framePane('province',region='left',width='300px')
        tb = frame.top.slotToolbar('*,selector,20,reloader')
        tb.selector.dbselect(value='^.regione',dbtable='glbl.regione',lbl='Regione')
        tb.reloader.button('reload',fire='.reload')
        iv = frame.includedView(struct='regione',autoSelect=True)
        iv.selectionStore(table='glbl.provincia',where='$regione=:r',
                          r='^.regione',_fired='^.reload')
        center = bc.contentPane(region='center',border='1px solid blue')
        form=iv.linkedForm(frameCode='provincia',loadEvent='onSelected',
                            formRoot=center,store_startKey='*norecord*',
                            store_onSaved='reload')
        form.testToolbar()
        #saver.addCallback('this.form.publish("load",{destPkey:result.getItem("pkey")});')
        fb = form.formbuilder(cols=2, border_spacing='4px', width="400px",fld_width="100%").formContent()
    
    def formCb(self,pane):
        pane.formbuilder(cols=2, border_spacing='4px', width="400px",fld_width="100%").formContent()
        
    

    def test_4_linkedForm_pane_nested(self,pane):
        mainform = pane.frameForm(frameCode='regione',height='500px',
                                center_widget='BorderContainer',table='glbl.regione',
                                store='recordCluster',store_startKey='*norecord*')
        tb = mainform.top.slotToolbar('selector,*,|,semaphore,|,formcommands,|,locker')
        tb.selector.dbselect(value='^.regione',dbtable='glbl.regione',lbl='Regione',
                             validate_onAccept='this.form.load({"destPkey":value});',parentForm=False)
        regione = mainform.contentPane(region='left',margin='2px')
        regione.div('!!Regione',background='darkblue',color='white',rounded_top=12,padding='4px')
        fb = regione.formbuilder(cols=2, border_spacing='3px')
        fb.field('sigla')
        fb.field('nome')
        fb.field('codice_istat')
        fb.field('ordine')
        fb.field('zona')
        province = mainform.framePane('province_regione',region='center',margin='2px',datapath='.#parent.provincia')
        province.top.slotToolbar('*,iv_add,iv_del',iv_add_parentForm=True,iv_del_parentForm=True)
        iv = province.includedView(struct='regione',autoSelect=True)
        iv.selectionStore(table='glbl.provincia',where='$regione=:r',r='^.#parent.record.sigla')
        form=iv.linkedForm(frameCode='provincia',loadEvent='onRowDblClick',
                            dialog_title='Provincia',dialog_height='300px',dialog_width='400px',store_onSaved='reload')
        form.testToolbar()
        saver = form.store.handler('save')        
        fb = form.formbuilder(cols=2, border_spacing='4px', width="400px",fld_width="100%").formContent()        
        fb.textbox(value='^.auxdata.prova',lbl='Prova')
        fb.textbox(value='^.auxdata.mia',lbl='Mia')
        fb.textbox(value='^.auxdata.foo.bar',lbl='Bar')


    
    def xxx(self,pane):
        tb.reloader.button('reload',fire='.reload')
        iv = frame.includedView(struct='regione',autoSelect=True)
        iv.selectionStore(table='glbl.provincia',where='$regione=:r',
                          r='^.regione',_fired='^.reload')
        center = bc.contentPane(region='center',border='1px solid blue')
        form=iv.linkedForm(frameCode='provincia',loadEvent='onSelected',
                            formRoot=center,store_startKey='*norecord*',
                            store_onSaved='reload')
        form.testToolbar()
    
        