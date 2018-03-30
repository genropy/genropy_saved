# -*- coding: UTF-8 -*-

# includedview_bagstore.py
# Created by Francesco Porcari on 2011-03-23.
# Copyright (c) 2011 Softwell. All rights reserved.

from gnr.core.gnrbag import Bag

class GnrCustomWebPage(object):
    dojo_source = True
    py_requires="gnrcomponents/testhandler:TestHandlerFull,th/th:TableHandler"
    
    def struttura_group(self,struct):
        r=struct.view().rows()
        r.fieldcell('@sigla_provincia.nome',width='20em')
        r.fieldcell('popolazione_residente',group_aggr='sum',width='10em')
        r.fieldcell('popolazione_residente',group_aggr='avg',width='10em')

    def test_0_firsttest(self,pane):
        bc = pane.borderContainer(height='400px',width='600px')
        bc.contentPane(region='top').dbSelect(value='^regione',dbtable='glbl.regione')
        center = bc.contentPane(region='center')
        center.groupByTableHandler(table='glbl.comune',struct=self.struttura_group,
                                condition='@sigla_provincia.regione LIKE :rg',condition_rg='^regione?=#v?#v:"%"',
                                border='1px solid silver')