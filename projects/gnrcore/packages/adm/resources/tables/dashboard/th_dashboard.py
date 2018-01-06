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
    py_requires="gnrcomponents/dashboard_component/dashboard_component:DashboardGallery"
    def th_form(self, form):
        bc = form.center.borderContainer()
        fb = bc.contentPane(region='top',datapath='.record').formbuilder(cols=3, border_spacing='4px')
        fb.field('pkgid')
        fb.field('code')
        fb.field('description')        
        bc.dashboardViewer(datapath='#FORM.dashboardEditor',
                            storepath='#FORM.record.data',edit=True,
                            region='center')



    def editorStruct(self,struct):
        r=struct.view().rows()
        r.cell('title',edit=True,width='15em',name='Title')
        r.cell('design',edit=dict(tag='filteringSelect',
        #validate_onAccept="""""""",
        values='headline,sidebar'),width='10em',name='Design')

    def th_options(self):
        return dict(dialog_height='400px', dialog_width='600px')

