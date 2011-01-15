# -*- coding: UTF-8 -*-

# formEditor.py
# Created by Francesco Porcari on 2011-01-12.
# Copyright (c) 2011 Softwell. All rights reserved.

"Test page description"
from gnr.web.gnrwebstruct import struct_method


class GnrCustomWebPage(object):
    py_requires="gnrcomponents/testhandler:TestHandlerFull,gnrcomponents/formhandler:FormHandler"

    def windowTitle(self):
        return 'Form handler'
         
    def test_0_formRecordPane(self,pane):
        """First test description"""
        tc = pane.tabContainer(height='400px')
        t1 = tc.contentPane(title='empty')
        t2 = tc.contentPane(title='withform').contentPane(_lazyBuild=True)
        form = t2.formPane(formId='myform',datapath='.provincia',disabled=False)
        form.recordClusterStore('glbl.provincia')
        
        form.top.slotToolbar('prova','navigation,|,selectrecord,|,*,|,semaphore,|,formcommands,|,locker')
        
        fb = form.content.formbuilder(cols=1, border_spacing='4px', width="100px", fld_width="100%",)
        fb.textbox(value="^.sigla", lbl="Sigla", validate_notnull=True)
        fb.textbox(value="^.nome", lbl="Nome", validate_notnull=True)
        fb.button('pippo',parentForm=True)
    
    def _test_2_paletteFormPane(self,pane):
        palette = pane.palettePane('province',title='Province',dockTo='*',maxable=True,
                                    _lazyBuild=True,
                                    background='red')
        form = palette.formPane(formId='provincie',datapath='.provincia',disabled=False)
        form.recordClusterStore('glbl.provincia')
        form.top.slotToolbar('prova','navigation,|,selectrecord,|,*,|,semaphore,|,formcommands,|,locker')
        fb = form.content.formbuilder(cols=1, border_spacing='4px', width="100px", fld_width="100%",)
        fb.textbox(value="^.sigla", lbl="Sigla", validate_notnull=True)
        fb.textbox(value="^.nome", lbl="Nome", validate_notnull=True)
        
    def __test_3_remotePaletteFormPane(self,pane):
        palette = pane.palettePane('province',title='Province',dockTo='*',maxable=True)
        form = palette.formPane(formId='provincie',datapath='.provincia',disabled=False)
        form.recordClusterStore('glbl.provincia')
        form.top.slotToolbar('prova','navigation,|,selectrecord,|,*,|,semaphore,|,formcommands,|,locker')
        fb = form.content.formbuilder(cols=1, border_spacing='4px', width="100px", fld_width="100%",)
        fb.textbox(value="^.sigla", lbl="Sigla", validate_notnull=True)
        fb.textbox(value="^.nome", lbl="Nome", validate_notnull=True)
        fb.button('pippo',parentForm=True)
                   
    @struct_method('prova_selectrecord')
    def prova_selectrecord(self,pane):
        pane.dbselect(value="^.prov",dbtable="glbl.provincia",parentForm=False,
                    validate_onAccept="this.form.publish('load',{destPkey:value});")
    
    def rpc_caricaDati(self, pkey, **kwargs):
        return self.db.table('glbl.provincia').recordAs(pkey, 'bag')

    def rpc_salvaDati(self, dati, **kwargs):
        print "Dati salvati:"
        print dati
    
    @struct_method
    def recordClusterStore(self,pane,table=None):
       #pane.dataRpc('dummy', 'saveRecordCluster', nodeId="myform_saver", dati="=.record",
       #           _onResult="genro.formById('myform').saved(); genro.formById('myform').load();")
        pane.attributes['form_table']=table or self.maintable
        pane.attributes['form_loadermethod'] = 'remoteClusterLoad'

