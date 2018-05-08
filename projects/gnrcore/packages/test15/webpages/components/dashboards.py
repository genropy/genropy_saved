# -*- coding: UTF-8 -*-

# Dashboards.py
# Created by Francesco Porcari on 2010-08-16.
# Copyright (c) 2010 Softwell. All rights reserved.

"""Dashboards"""
from gnr.core.gnrdecorator import public_method

class GnrCustomWebPage(object):
    py_requires = "gnrcomponents/testhandler:TestHandlerBase,th/th:TableHandler,gnrcomponents/dashboard_component/dashboard_component:DashboardItem"

    def windowTitle(self):
        return 'Dashboards'




        
    def test_1_dashboardItem(self,pane):
        bc = pane.borderContainer(height='400px',width='800px')
        left = bc.contentPane(region='left',width='200px',background='lime')
        top = bc.contentPane(region='top')
        fb = top.formbuilder()
        fb.data('.table','glbl.provincia')
        fb.filteringSelect(value='^.table',lbl='Table',values='glbl.provincia,glbl.regione')
        
        bc.contentPane(region='center').dashboardItem(table='adm.dashboard',
                            itemName='tableview',itempar_table='^.table')
    
    def test_2_remoteLayout(self,pane):
        bc = pane.borderContainer(height='400px',width='800px')
        left = bc.contentPane(region='left',width='200px',background='lime')
        top = bc.contentPane(region='top')
        fb = top.formbuilder()
        fb.button('Build',fire='.build')

        bc.contentPane(region='center').remote(self.remoteLayout,_fired='^.build')
  
    @public_method
    def remoteLayout(self,pane):
        bc = pane.contentPane().borderContainer()
        bc.contentPane(region='top').div(height='20px',background='gray')
        sc = bc.stackContainer(region='center')
        sc.contentPane(title='pippo').selectionViewer(table='adm.user')
        sc.contentPane(title='paperino')
        

    