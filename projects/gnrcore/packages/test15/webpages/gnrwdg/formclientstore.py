# -*- coding: UTF-8 -*-

# formclientstore.py
# Created by Francesco Porcari on 2012-05-12.
# Copyright (c) 2012 Softwell. All rights reserved.

from gnr.core.gnrbag import Bag

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
        
    def test_0_bagstore(self,pane):
        """First test description"""
        myform = pane.frameForm(frameCode='myform',height='300px',datapath='.myform')
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
        
        
        