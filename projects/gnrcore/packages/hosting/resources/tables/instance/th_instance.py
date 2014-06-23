#!/usr/bin/python
# -*- coding: UTF-8 -*-

from gnr.web.gnrbaseclasses import BaseComponent
from gnr.core.gnrdecorator import public_method

class View(BaseComponent):

    def th_struct(self,struct):
        r = struct.view().rows()
        r.fieldcell('code')
        r.fieldcell('description')
        r.fieldcell('repository_name')
        r.fieldcell('path')
        r.fieldcell('site_path')
        r.fieldcell('slot_configuration')
        r.fieldcell('hosted_data')
        r.fieldcell('client_id')

    def th_order(self):
        return 'code'

    def th_query(self):
        return dict(column='code', op='contains', val='')


    @public_method
    def th_applymethod(self, selection, **kwargs):  
        def apply_row(row):
            instance_exists = self.db.packages['hosting'].instance_exists(row['code'])
            site_exists = self.db.packages['hosting'].site_exists(row['code'])
            if site_exists and instance_exists:
                return dict(create='<div class="greenLight"></div>')
            else:
                return dict(create='<div class="yellowLight"></div>')
        selection.apply(apply_row)

class Form(BaseComponent):
    py_requires='gnrcomponents/framegrid:BagGrid,hosted:HostedInstance'

    def th_form(self, form):
        bc = form.center.borderContainer(datapath='.record')
        fb = bc.contentPane(region='top').formbuilder(cols=2, border_spacing='4px')
        fb.field('code')
        fb.field('client_id')

        fb.field('description')
        fb.field('repository_name')
        fb.field('path')
        fb.field('site_path')
        #fb.field('slot_configuration')
        #fb.field('hosted_data')
        #fb.field('last_update_log',colspan='2',tag='simpleTextArea',width='600px',height='500px')
        tc = bc.tabContainer(region='center')
        self.main_instancetab(tc.borderContainer(title='Instance'))
        self.hosted_tabs(tc)

    def main_instancetab(self, bc):
        pane = bc.contentPane(region='top')
        fb = pane.formbuilder(cols=2, border_spacing='6px')
        fb.field('code', width='15em', lbl='!!Instance Name',validate_notnull=True,disabled='^#FORM.record.active')
        fb.button('Activate',action='FIRE #FORM.activate_instance',hidden='^#FORM.record.id?=!#v',disabled='^#FORM.controller.changed')
        fb.dataRpc('dummy',self.activateInstance,_fired='^#FORM.activate_instance',_onResult='this.form.reload();',instance_id='=#FORM.record.id',_lockScreen=True)
        bc.contentPane(region='center',datapath='#FORM').inlineTableHandler(relation='@slots',viewResource='ViewFromInstance',margin='2px',pbl_classes=True)

    @public_method
    def activateInstance(self,instance_id=None):
        instanctbl = self.db.table('hosting.instance')
        record = instanctbl.record(pkey=instance_id,for_update=True).output('dict')
        instanctbl.activate_instance(record)
        oldrecord = dict(record)
        record['active'] = True
        instanctbl.update(record,oldrecord)

    @public_method
    def th_onLoading(self, record, newrecord, loadingParameters, recInfo):
        instance_exists = self.db.packages['hosting'].instance_exists(record['code'])
        site_exists = self.db.packages['hosting'].site_exists(record['code'])
        record.setItem('$instance_exists', instance_exists)
        record.setItem('$site_exists', site_exists)

    def hosted_tabs(self,tc):
        for pkgname, handler in [(c.split('_')[1], getattr(self, c)) for c in dir(self) if
                                 c.startswith('hostedinstance_')]:
            handler(tc.contentPane(datapath='.hosted_data.%s' % pkgname, title=self.db.packages[pkgname].name_long,
                                   nodeId='hosted_instance_data_%s' % pkgname,
                                   sqlContextName='sql_record_hosted_instance_%s' % pkgname,
                                   sqlContextRoot='instances.dlg.record.hosted_data.%s' % pkgname))


class FormFromClient(Form):
    py_requires='gnrcomponents/framegrid:BagGrid,hosted:HostedInstance'
    def th_form(self,form):
        tc = form.center.tabContainer(datapath='.record',margin='2px')
        self.main_instancetab(tc.borderContainer(title='Info'))
        self.hosted_tabs(tc)




    def th_options(self):
        return dict(dialog_height='400px', dialog_width='600px')
