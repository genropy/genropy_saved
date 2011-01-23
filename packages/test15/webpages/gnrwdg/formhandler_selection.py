# -*- coding: UTF-8 -*-

# formhandler_selection.py
# Created by Francesco Porcari on 2011-01-18.
# Copyright (c) 2011 Softwell. All rights reserved.

from gnr.web.gnrwebstruct import struct_method

"Test formhandler selection store"
class GnrCustomWebPage(object):
    py_requires="""gnrcomponents/testhandler:TestHandlerFull,gnrcomponents/formhandler:FormHandler,
                  gnrcomponents/palette_manager:PaletteManager"""
    
    @struct_method
    def formTester(self,pane,formId=None,**kwargs):
        form = pane.formPane(formId=formId,datapath='.provincia',**kwargs)
        form.recordClusterStore('glbl.provincia',storeType='Collection',
                                storepath='#province_grid.store')
        form.top.slotToolbar('prova','navigation,*,|,semaphore,|,formcommands,|,locker')
        fb = form.content.formbuilder(cols=1, border_spacing='4px', width="300px", fld_width="100%")
        fb.field('sigla')
        fb.field('regione')
        fb.field('nome')
        fb.field('codice_istat')
        fb.field('ordine')
        fb.field('ordine_tot')
        fb.field('cap_valido')
        return form

         
    def _test_0_base(self,pane):
        bc = pane.borderContainer(height='250px')
        left = bc.borderContainer(region='left',width='300px',datapath='.grid')
        center = bc.contentPane(region='center',border='1px solid blue').formTester(formId='provincia')
        
       # bc.selectionStore('province_in_regione',table='glbl.provincia',where='$regione=:r',r='=.regione')        

        paneGrid = bc.paneGrid('province',region='left',struct='regione',#store='province_in_regione',
                                autoSelect=True,selectedId='.selectedPkey',
                                selfsubscribe_onSelectedRow='genro.formById("provincia").publish("load",{destPkey:$1.selectedId});',
                                subscribe_form_provincia_onLoaded="this.widget.selectByRowAttr('_pkey',$1.pkey)")
                                
        paneGrid.selectionStore(table='glbl.provincia',where='$regione=:r',r='=.regione')        

        paneGrid.slotToolbar('gridtoolbar','*,selector')
                
    def _test_0_includedview_store(self,pane):
        pane = pane.framePane(height='200px')
        pane.slotToolbar('gridtoolbar','selector,*,searchOn',searchOn=True,wdgNodeId='mygrid',side='top')
        pane.includedView(nodeId='mygrid',struct='regione',relativeWorkspace=True,datapath='.tblprovince'
                          ).selectionStore(table='glbl.provincia',where='$regione=:r',r='=#selector.regione')
        
    def test_1_includedview_store(self,pane):
        pane.selectionStore(storeCode='provinceRegione',table='glbl.provincia',where='$regione=:r',r='=#selector.regione')
        pane = pane.framePane(height='200px')
        pane.slotToolbar('gridtoolbar','selector,*,searchOn',searchOn=True,wdgNodeId='mygrid',side='top')
        pane.includedView(nodeId='mygrid',struct='regione',relativeWorkspace=True,datapath='.tblprovince',
                         storepath='gnr.stores.provinceRegione.data',store='provinceRegione')

        
    @struct_method('gridtoolbar_selector')
    def gridtoolbar_selector(self,pane,wdgNodeId=None,**kwargs):
        fb = pane.formbuilder(cols=1, border_spacing='2px')
        fb.dbselect(value='^.regione',dbtable='glbl.regione',lbl='Regione',nodeId='selector',
                     validate_onAccept='genro.wdgById("mygrid").reload();')


    
        