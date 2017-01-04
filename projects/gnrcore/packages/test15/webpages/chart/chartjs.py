# -*- coding: UTF-8 -*-

# Created by Francesco Porcari on 2010-12-27.
# Copyright (c) 2010 Softwell. All rights reserved.
 
"""Test Protovis"""

from gnr.core.gnrbag import Bag 
class GnrCustomWebPage(object):
    py_requires="gnrcomponents/testhandler:TestHandlerFull,th/th:TableHandler,js_plugins/chartjs/chartjs:ChartManager"

    def source_viewer_open(self):
        return False
    def test_0_simple(self, pane):
        pane.chartjs(nodeId='testchart_0',chartType='bar',data={
                'ylabels': ["yRed", "yBlue", "yYellow", "yGreen", "yPurple", "yOrange"],
                'xLabels': ["xRed", "xBlue", "xYellow", "xGreen", "xPurple", "xOrange"],
                'datasets': [{
                    'label': '# of Votes',
                    'data': [12, 19, 3, 5, 2, 3],
                    'backgroundColor': 'rgba(255, 99, 132, 0.2)',
                    'borderColor': 'rgba(255,99,132,1)',
                    'borderWidth': 1
                },{
                    'label': '# of Votes last year',
                    'data': [10, 16, 8, 9, 6, 3],
                    'backgroundColor': 'rgba(54, 162, 235, 0.2)',
                    'borderColor': 'rgba(54, 162, 235, 1)',
                    'borderWidth': 1
                }]
            },options={
                'scales': {
                    'yAxes': [{
                        'ticks': {
                            'beginAtZero':True
                        }
                    }]
                }},
            height='300px',width='600px',border='1px solid silver')
        return
        pane.chartjs(nodeId='testchart_2',chartType='line',data={
                'labels': ["Red", "Blue", "Yellow", "Green", "Purple", "Orange"],
                'datasets': [{
                    'label': '# of Votes',
                    'data': [12, 19, 3, 5, 2, 3],
                    'backgroundColor': 'rgba(255, 99, 132, 0.2)',
                    'borderColor': 'rgba(255,99,132,1)',
                    'borderWidth': 1
                },{
                    'label': '# of Votes last year',
                    'data': [10, 16, 8, 9, 6, 3],
                    'backgroundColor': 'rgba(54, 162, 235, 0.2)',
                    'borderColor': 'rgba(54, 162, 235, 1)',
                    'borderWidth': 1
                }]
            },options={
                'scales': {
                    'yAxes': [{
                        'ticks': {
                            'beginAtZero':True
                        }
                    },{
                        'ticks': {
                            'beginAtZero':True,
                            'max':100
                        }
                    },{
                        'ticks': {
                            'min':-8,
                            'beginAtZero':False,
                            'max':70
                        }
                    }]
                }},
            height='300px',width='600px',border='1px solid silver')

    def test_1_glbl(self,pane):
        bc = pane.borderContainer(height='500px',width='900px',_anchor=True)
        fb = bc.contentPane(region='top').formbuilder(cols=1,border_spacing='3px')
        fb.dbSelect(value='^.regione',dbtable='glbl.regione',lbl='Regione')
        fb.dataFormula('.regione','reg',reg='LOM',_onStart=True)
        th = bc.contentPane(region='left',width='50%').plainTableHandler(table='glbl.provincia',
                                                condition='$regione=:reg',
                                                condition_reg='^#ANCHOR.regione',
                                                viewResource='ViewTestGraph')
        th.view.top.bar.replaceSlots('searchOn','chartjs,10,searchOn')



    def test_2_bagDataValue(self, pane):
        pane.data('.data',self.getTestData())
        bc = pane.borderContainer(height='600px',width='800px',_anchor=True)
        frame = bc.bagGrid(storepath='#ANCHOR.data',region='center',struct=self.bmiStruct)
        frame.top.bar.replaceSlots('delrow','chartjs,delrow')

    def bmiStruct(self,struct):
        r = struct.view().rows()
        r.cell('nome',edit=True,name='Nome')
        r.cell('eta',edit=True,name=u'Età',dtype='L')
        r.cell('peso',edit=True,name='Peso',dtype='L')
        r.cell('altezza',edit=True,name='Altezza',dtype='L')
        r.cell('bmi',formula='(peso||0)/((altezza||1)*(altezza||1))',name='BMI',dtype='L')

    def getTestData(self):
        result = Bag()
        result.setItem('r_0',Bag(dict(nome='Mario Rossi',eta=30,peso=80,altezza=190)))
        result.setItem('r_1',Bag(dict(nome='Luigi Bianchi',eta=38,peso=90,altezza=180)))
        result.setItem('r_2',Bag(dict(nome='Rossella Albini',eta=22,peso=60,altezza=170)))
        return result

