#!/usr/bin/python
# -*- coding: utf-8 -*-

from gnr.web.gnrbaseclasses import BaseComponent
from gnr.core.gnrdecorator import public_method

class View(BaseComponent):
    def th_hiddencolumns(self):
        return '$service_identifier'


    def th_struct(self,struct):
        r = struct.view().rows()
        r.fieldcell('service_name')
        r.fieldcell('service_type')
        r.fieldcell('implementation')
        r.fieldcell('parameters',width='40em')
        #r.fieldcell('extrainfo',width='30em')

    def th_order(self):
        return 'service_identifier'

    def th_query(self):
        return dict(column='service_identifier', op='contains', val='')

    def th_options(self):
        #addrow=[(service_type,dict(service_type=service_type)) for service_type in service_types]
        return dict(addrow=self.db.table('sys.service').getAvailableServiceTree())



class Form(BaseComponent):

    def th_form(self, form):
        bc = form.center.borderContainer(datapath='.record')
        fb = bc.contentPane(region='top').formbuilder(cols=2, border_spacing='4px')
        fb.field('service_type',disabled=True)
        fb.field('implementation',disabled=True)
        fb.field('service_name',colspan=2,validate_notnull=True,width='100%',disabled=True)
        #fb.field('daemon',colspan=1,html_label=True)
        fb.field('disabled',colspan=1,html_label=True)

        center = bc.roundedGroupFrame(title='Parameters',region='center')
        center.center.contentPane().remote(self.buildServiceParameters,service_type='=.service_type',implementation='=.implementation',
                                                    _if="service_type && implementation",
                                                    _fired='^#FORM.controller.loaded')


    @public_method
    def buildServiceParameters(self,pane,service_type=None,implementation=None,**kwargs):
        mixinpath = '/'.join(['services',service_type,implementation])
        self.mixinComponent('%s:ServiceParameters' %mixinpath,safeMode=True)
        if hasattr(self,'service_parameters'):
            self.service_parameters(pane,datapath='.parameters')

    def th_options(self):
        return dict(form_add=self.db.table('sys.service').getAvailableServiceTree(),
                    defaultPrompt=dict(title='!!New service',
                                    fields=[dict(value='^.service_name',lbl='Service name')],doSave=True))

    #def th_options(self):
    #    return dict(dialog_height='400px', dialog_width='600px',addrow=[(service_type,dict(service_type=service_type)) for service_type in service_types])
