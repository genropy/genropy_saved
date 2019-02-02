# -*- coding: utf-8 -*-

# Dashboards.py
# Created by Francesco Porcari on 2010-08-16.
# Copyright (c) 2010 Softwell. All rights reserved.

"""Dashboards"""
from builtins import object
from gnr.core.gnrdecorator import public_method

class GnrCustomWebPage(object):
    py_requires = "gnrcomponents/testhandler:TestHandlerBase,dashboard_component/dashboard_component:DashboardItem"

    def windowTitle(self):
        return 'Dashboards'

    def test_1_dashboardItem(self,pane):
        bc = pane.borderContainer(height='400px',width='800px')
        left = bc.contentPane(region='left',width='200px',background='lime')
        top = bc.contentPane(region='top')
        bc.contentPane(region='center').dashboardItem(table='fatt.cliente',
                            itemName='edit_clienti')