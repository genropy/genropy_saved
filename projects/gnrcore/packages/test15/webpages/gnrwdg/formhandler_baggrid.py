# -*- coding: UTF-8 -*-

# includedview_bagstore.py
# Created by Francesco Porcari on 2011-03-23.
# Copyright (c) 2011 Softwell. All rights reserved.

from gnr.core.gnrbag import Bag

class GnrCustomWebPage(object):
    dojo_source = True
    css_requires='public'
    py_requires="""gnrcomponents/testhandler:TestHandlerFull,gnrcomponents/framegrid:BagGrid,gnrcomponents/formhandler:FormHandler"""
    
    def test_0_firsttest(self,pane):
        """First test description"""
        bc = pane.borderContainer(height='600px',datapath='.bh')

        top = bc.contentPane(region='top',height='300px',datapath='.view')
        top.data('.dati',self.getDati())

        top.dataController('SET gridstore = dati.deepCopy();',dati='=.dati',_fired='^zzz',_onStart=True)
        frame = top.bagGrid(frameCode='test_view',title='Test',struct=self.gridstruct,height='300px',
                            table='glbl.localita',storepath='gridstore')
        frame.bottom.button('Load',fire='zzz')
        center = bc.contentPane(region='center')

        myform = frame.grid.linkedForm(frameCode='test_form',
                                 datapath='.form',loadEvent='onSelected',
                                 childname='form',formRoot=center,store='memory',store_locationpath='gridstore')


        center = myform.center.contentPane(datapath='.record')
        fb = center.formbuilder(cols=1, border_spacing='3px')
        fb.dbselect(value='^.provincia',lbl='Provincia',dbtable='glbl.provincia')

        fb.numbertextbox(value='^.qty',lbl='Quantitativo')
        fb.numbertextbox(value='^.colli',lbl='Colli',validate_notnull=True,validate_notnull_error='!!Required')
        myform.top.slotToolbar('*,delete,add,save,semaphore')
#


        

    def gridstruct(self, struct):
        r = struct.view().rows()
        r.fieldcell('provincia',edit=dict(selected_codice_istat='.cist'),table='glbl.provincia',caption_field='provincia_nome')
        r.cell('qty',dtype='L',name='Quantitativo',width='5em')  
        r.cell('colli',dtype='L',name='Colli',width='5em')  
        r.cell('Totale',dtype='L',name='Colli',width='5em')  
        r.cell('cist',name='Codice istat')

    def getDati(self):
        result = Bag()
        result.setItem('r_0',Bag(dict(provincia = 'MI',qty=13,provincia_nome='Milano',cist='044')))
        result.setItem('r_1',Bag(dict(provincia = 'CO',qty=22,provincia_nome='Como',cist='039')))
        return result

