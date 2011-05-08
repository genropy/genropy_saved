# -*- coding: UTF-8 -*-

# test_iframe_inside.py
# Created by Francesco Porcari on 2011-02-14.
# Copyright (c) 2011 Softwell. All rights reserved.

from gnr.web.gnrwebstruct import struct_method

"iframe_inside"

class GnrCustomWebPage(object):
    py_requires='gnrcomponents/formhandler:FormHandler'
    dojo_source=True
    
    def windowTitle(self):
        return 'Inside frame'
         
    @struct_method
    def testToolbar(self,form,startKey=None):
        tb = form.top.slotToolbar('*,|,semaphore,|,formcommands,|,locker',border_bottom='1px solid silver')
        
    @struct_method
    def formContent(self,fb):
        fb.field('sigla')
        fb.field('regione')
        fb.field('nome')
        fb.field('codice_istat')
        fb.field('ordine')
        fb.field('ordine_tot')
        fb.field('cap_valido')
        return fb
        
    def main(self,pane,**kwargs):
        form = pane.frameForm(frameCode='baseform',border='1px solid silver',datapath='form',
                            rounded_bottom=10,height='180px',width='600px',
                            pkeyPath='.prov',background='white',
                            formsubscribe_onDismissed='genro.publish({"topic":"switchPage","parent":true,nodeId:"maintab"},0);')
        form.dataController("this.form.publish('load',{destPkey:pkey})",pkey="^pkey")
        form.testToolbar()
        store = form.formStore(table='glbl.provincia',storeType='Item',
                               handler='recordCluster',startKey='*norecord*',onSaved='dismiss')
            
        form.center.contentPane(datapath='.record').formbuilder(cols=2, border_spacing='3px').formContent()
        