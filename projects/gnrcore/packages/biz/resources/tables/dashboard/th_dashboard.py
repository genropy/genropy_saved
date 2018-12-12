#!/usr/bin/python
# -*- coding: utf-8 -*-

from gnr.web.gnrbaseclasses import BaseComponent
from gnr.core.gnrdecorator import public_method

class View(BaseComponent):

    def th_struct(self,struct):
        r = struct.view().rows()
        r.fieldcell('pkgid')
        r.fieldcell('code')
        r.fieldcell('description')

    def th_order(self):
        return 'dashboard_key'

    def th_query(self):
        return dict(column='dashboard_key', op='contains', val='')

    def th_options(self):
        return dict()


class Form(BaseComponent):
    py_requires="dashboard_component/dashboard_component:DashboardGallery"
    def th_form(self, form):
    
        bc = form.center.borderContainer()
        fb = bc.contentPane(region='top',datapath='.record').formbuilder(cols=2, border_spacing='4px')
        fb.field('pkgid',disabled=True)
        fb.field('code',disabled=True)
        fb.field('description',colspan=2,width='100%')   
        tc = bc.tabContainer(region='center',margin='2px')
        tc.dashboardViewer(title='Dashboards',datapath='#FORM.dashboardEditor',
                            storepath='#FORM.record.data',edit=True)
        bc = tc.borderContainer(title='Configurations')
        bc.channelsViewer(region='center',storepath='#FORM.record.data.channels',datapath='#FORM.dashboardChannels')
        bc.itemsViewer(region='bottom',height='400px',storepath='#FORM.record.data.items',datapath='#FORM.dashboardItems') 

    def th_options(self):
        return dict(dialog_height='400px', dialog_width='600px',
                    defaultPrompt=dict(title='New dashboard',
                                    fields=[dict(value='^.pkgid',tag='PackageSelect',lbl='Package',validate_notnull=True),
                                                dict(value='^.code',tag='Textbox',lbl='Code',validate_notnull=True)]))


class FormIncluded(Form):
    def th_form(self, form):
        bc = form.center.borderContainer()
        bc.dataController("""
        SET #FORM.from_table = _subscription_kwargs.from_table;
        SET #FORM.from_pkey = _subscription_kwargs.from_pkey;
        """,subscribe_main_form_open=True)
        tc = bc.tabContainer(region='center',margin='2px')
        tc.dashboardViewer(title='Dashboards',datapath='#FORM.dashboardEditor',
                            storepath='#FORM.record.data',edit=True)
        bc = tc.borderContainer(title='Configurations')
        bc.channelsViewer(region='center',storepath='#FORM.record.data.channels',datapath='#FORM.dashboardChannels')
        bc.itemsViewer(region='bottom',height='400px',storepath='#FORM.record.data.items',datapath='#FORM.dashboardItems') 
    
    def th_options(self):
        return dict(modal=True)