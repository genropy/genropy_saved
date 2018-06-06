#!/usr/bin/python
# -*- coding: UTF-8 -*-

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



class Form(BaseComponent):
    py_requires="dashboard_component/dashboard_component:DashboardGallery"
    def th_form(self, form):
        bc = form.center.borderContainer()
        fb = bc.contentPane(region='top',datapath='.record').formbuilder(cols=2, border_spacing='4px')
        fb.field('pkgid',validate_notnull=True,
                    tag='filteringSelect',
                    values=','.join(self.db.application.packages.keys()))
        fb.field('code',validate_notnull=True,unmodifiable=True)
        fb.field('description',colspan=2,width='100%')   
        tc = bc.tabContainer(region='center',margin='2px')
        tc.dashboardViewer(title='Dashboards',datapath='#FORM.dashboardEditor',
                            storepath='#FORM.record.data',edit=True)
        tc.itemsViewer(title='Items',storepath='#FORM.record.data.items',datapath='#FORM.dashboardItems') 




    def editorStruct(self,struct):
        r=struct.view().rows()
        r.cell('title',edit=True,width='15em',name='Title')
        r.cell('design',edit=dict(tag='filteringSelect',
        #validate_onAccept="""""""",
        values='headline,sidebar'),width='10em',name='Design')

    def th_options(self):
        return dict(dialog_height='400px', dialog_width='600px')

