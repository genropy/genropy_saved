# -*- coding: utf-8 -*-

import datetime
from gnr.core.gnrdecorator import public_method

class GnrCustomWebPage(object):
    py_requires = """gnrcomponents/testhandler:TestHandlerFull,
                    gnrcomponents/userobject/userobject_editor:GroupByEditor"""
    
    def test_1_print_preview(self, pane):
        bc = pane.borderContainer(height='700px')
        top = bc.contentPane(region='top',height='50%',border_bottom='1px solid silver')
        th = top.plainTableHandler(table='fatt.fattura',virtualStore=True,extendedQuery=True,datapath='.myth')
        th.dataFormula('.queryBag',
                        """new gnr.GnrBag({where:_queryWhere.deepCopy(),limit:_queryLimit,customOrderBy:_customOrderBy});""",
                        _queryWhere='^.view.query.where',
                        _queryLimit='^.view.query.queryLimit',
                        _customOrderBy='^.view.query.customOrderBy')

        bc.contentPane(region='center'
                        ).documentFrame(resource='fatt.fattura:html_res/print_gridres',
                        pkey='*',html=True,
                        currentGridStruct='==genro.wdgById("{gridId}").getExportStruct();'.format(gridId=th.view.grid.attributes['nodeId']),
                        currentQuery='=.myth.queryBag',
                        _fired='^.myth.view.runQueryDo',_delay=100)

    def test_2_print_preview(self, pane):
        bc = pane.borderContainer(height='700px')
        top = bc.contentPane(region='top',height='50%',border_bottom='1px solid silver')
        th = top.plainTableHandler(table='fatt.fattura',virtualStore=True,extendedQuery=True,datapath='.master')
        center =bc.contentPane(region='center')
        center.plainTableHandler(table='fatt.fattura',virtualStore=True,datapath='.slave')