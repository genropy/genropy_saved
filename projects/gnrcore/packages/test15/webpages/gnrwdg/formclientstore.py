# -*- coding: UTF-8 -*-

# formclientstore.py
# Created by Francesco Porcari on 2012-05-12.
# Copyright (c) 2012 Softwell. All rights reserved.

from gnr.core.gnrbag import Bag
from gnr.web.gnrwebstruct import struct_method


"Store memory"
class GnrCustomWebPage(object):
    py_requires="gnrcomponents/testhandler:TestHandlerFull,gnrcomponents/formhandler:FormHandler"

    def windowTitle(self):
        return ''
    
    
    def memoryStoreData(self):
        result = Bag()
        result.setItem('r_0',Bag(dict(name='Mario',surname='Merola',age=35)))
        result.setItem('r_1',Bag(dict(name='Luigi',surname='Camigi',age=22)))
        result.setItem('r_2',Bag(dict(name='Salvo',surname='De Bobbis',age=79)))
        return result
        


    @struct_method
    def testToolbar(self,form,startKey=None):
        left = 'selector,|,' if not startKey else ''
        tb = form.top.slotToolbar('%s *,4,semaphore,4,formcommands,4,locker' %left,border_bottom='1px solid silver')
        if not startKey:
            fb = tb.selector.formbuilder(cols=1, border_spacing='1px')
            fb.dbselect(value="^.prov",dbtable="glbl.provincia",parentForm=False,#default_value='MI',
                                        validate_onAccept="if(userChange){this.form.publish('load',{destPkey:value})};",
                                        lbl='Provincia')
        return tb
        

    def test_0_subform(self,pane):
        "Test FrameForm"
        form = pane.frameForm(frameCode='provincia_1',border='1px solid silver',datapath='.form',
                              rounded_bottom=10,height='300px',width='600px',pkeyPath='.prov')
        form.testToolbar()
        form.formStore(table='glbl.provincia',storeType='Item',handler='recordCluster',startKey='*norecord*',onSaved='reload')
        bc = form.center.borderContainer()
        fb = bc.contentPane(region='top').formbuilder(cols=1,border_spacing='3px',datapath='.record')
        fb.field('sigla')
        fb.field('regione')

        fb.field('nome',disabled=True)
        fb.field('codice_istat',disabled=True)

        fb.field('ordine')
        fb.field('ordine_tot')
        fb.field('cap_valido')
        
        subform = bc.contentPane(region='center').frameForm(frameCode='sottocampi',datapath='#FORM.sottocampi',store='subform')
        bar = subform.top.slotBar('*,semaphore,loadbtn,savebtn')
        bar.loadbtn.button('Load',action='this.form.load();')
        bar.savebtn.button('Save',action='this.form.save();')
        pane = subform.record
        fb = pane.formbuilder(cols=1,border_spacing='3px')
        fb.field('nome',validate_len=':10')
        fb.field('codice_istat')

    def test_1_bagstore_collection(self,pane):
        """First test description"""
        myform = pane.frameForm(frameCode='myform_1',height='300px',datapath='.myform')
        pane.data('.collection',self.memoryStoreData())
        center = myform.center.contentPane(datapath='.record')
        fb = center.formbuilder(cols=1, border_spacing='3px')
        fb.textbox(value='^.name',lbl='Name')
        fb.textbox(value='^.surname',lbl='Surname',validate_notnull=True,validate_notnull_error='!!Required')
        bar = myform.top.slotToolbar('loadpath,*,delete,add,save,semaphore')
        loadfb = bar.loadpath.formbuilder(cols=2, border_spacing='2px')
        loadfb.filteringSelect(value='^.pkeyToLoad',storepath='.#parent.collection',
                width='20em',parentForm=False,storeid='#k',storecaption='.surname')
        loadfb.button('Load',action=""" if(pkey){
                                this.form.load({destPkey:pkey});
                            }
                            """,pkey='=.pkeyToLoad')
        myform.formstore(handler='memory',locationpath='.#parent.collection')

        
        