# -*- coding: UTF-8 -*-

# Dashboards.py
# Created by Francesco Porcari on 2010-08-16.
# Copyright (c) 2010 Softwell. All rights reserved.

"""Dashboards"""
from gnr.core.gnrdecorator import public_method

class GnrCustomWebPage(object):
    py_requires = "gnrcomponents/testhandler:TestHandlerBase,th/th:TableHandler,dashboard_component/dashboard_component:DashboardItem"

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