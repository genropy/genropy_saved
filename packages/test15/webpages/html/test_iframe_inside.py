# -*- coding: UTF-8 -*-

# test_iframe.py
# Created by Francesco Porcari on 2011-02-14.
# Copyright (c) 2011 Softwell. All rights reserved.

from gnr.web.gnrwebstruct import struct_method

"Test page description"
class GnrCustomWebPage(object):
    py_requires='gnrcomponents/formhandler:FormHandler'

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
        #pane.dataController("parent.genro.setData('frame.test1.page_id',genro.page_id)",_onStart=True)
        form = pane.frameForm(frameCode='baseform',border='1px solid silver',datapath='form',
                            rounded_bottom=10,height='180px',width='600px',
                            pkeyPath='.prov',background='white')
        form.dataController("this.form.publish('load',{destPkey:pkey})",pkey="^pkey")
        form.testToolbar()
        store = form.formStore(storepath='.record',table='glbl.provincia',storeType='Item',
                               handler='recordCluster',startKey='*norecord*',onSaved='reload')
        store.handler('save').addCallback('parent.genro.setData("currentPage","selector")')
        form.formbuilder(cols=2, border_spacing='3px').formContent()    
        