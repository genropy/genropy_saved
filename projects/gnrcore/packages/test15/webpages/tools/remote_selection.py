# -*- coding: utf-8 -*-
# 

from gnr.core.gnrdecorator import public_method
from gnr.core.gnrbag import Bag


class GnrCustomWebPage(object):
    py_requires = "gnrcomponents/testhandler:TestHandlerFull,gnrcomponents/framegrid:FrameGrid"
    
    def test_1_plain(self, pane):
        """Set in external store"""
        bc = pane.borderContainer(height='400px',datapath='main')
        frame = bc.contentPane(region='center').frameGrid(frameCode='testmio',struct=self.struct_cliente,
                                    #autoToolbar=False,
                                    datapath='.view')
        frame.grid.rpcStore(rpcmethod=self.testData,_onStart=True)    

    def struct_cliente(self,struct):
        r = struct.view().rows()
        r.cell('code',name='Code')
        r.cell('description',name='Description')


    def test_2_bis(self, pane):
        bc = pane.borderContainer(height='400px',datapath='main')
        frame = bc.contentPane(region='center').frameGrid(frameCode='selectionsimple',struct=self.struct_cliente,
                                    #autoToolbar=False,
                                    datapath='.view')
        frame.grid.selectionStore(table='uke.company',_rpchost="http://127.0.0.1:8090/",_fired='^runtest',_POST=False)
        bc.contentPane(region='top').button('Run',fire='runtest')


    @public_method
    def testData(self,columns=None,**kwargs):
        result = self.site.callExternalUrl('http://127.0.0.1:8090/uke/commands/getRemoteSelection',table='uke.company',columns=columns)
        return Bag(result)




    def test_3_bis(self, pane):
        bc = pane.borderContainer(height='400px',datapath='main')
        frame = bc.contentPane(region='center').frameGrid(frameCode='regioni',struct=self.struct_regioni,
                                    #autoToolbar=False,
                                    datapath='.view')
        frame.grid.selectionStore(table='glbl.regione',_rpchost="http://127.0.0.1:8090/",
                                _fired='^runtest',_POST=False)
        bc.contentPane(region='top').button('Run',fire='runtest')

    def struct_regioni(self,struct):
        r = struct.view().rows()
        r.cell('nome', width='20em')
        r.cell('sigla',width='3em')
        r.cell('codice_istat',width='7em',sortable=False)
        r.cell('zona',width='100%')

