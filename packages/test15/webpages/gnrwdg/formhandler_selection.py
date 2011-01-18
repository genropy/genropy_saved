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
        form.recordClusterStore('glbl.provincia',storeType='Collection',storepath='#province_grid.store')
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

         
    def test_0_base(self,pane):
        bc = pane.borderContainer(height='250px')
        left = bc.borderContainer(region='left',width='300px',datapath='.grid')
        center = bc.contentPane(region='center',border='1px solid blue').formTester(formId='provincia')
        toolbar = left.contentPane(region='top').slotToolbar('gridtoolbar','*,searchOn')
        toolbar.slot_searchOn.dbselect(value='^.regione',dbtable='glbl.regione',
                                       validate_onAccept='genro.wdgById("province_grid").reload();')
        gridpane = left.contentPane(region='center')
        
        gridpane.includedview(storepath='.store',struct='regione',nodeId='province_grid',
                             relativeWorkspace=True,table='glbl.provincia',
                             connect_onRowDblClick='genro.formById("provincia").publish("load",{destPkey:this.widget.rowIdByIndex($1.rowIndex)});')
        bc.selectionStore(storepath='.grid.store',table='glbl.provincia',where='$regione=:r',
                                r='=.grid.regione',gridId='province_grid')

        
        #gridpane.selectionStore(table='glbl.provincia',gridId='province_grid',)
    

    
        