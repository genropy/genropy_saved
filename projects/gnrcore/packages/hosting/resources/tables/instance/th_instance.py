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
        return dict(column='code', op='contains', val='%')


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

    def th_form(self, form):
        pane = form.record
        fb = pane.formbuilder(cols=2, border_spacing='4px')
        fb.field('code')
        fb.field('description')
        fb.field('repository_name')
        fb.field('path')
        fb.field('site_path')
        fb.field('slot_configuration')
        fb.field('hosted_data')
        fb.field('client_id')


class FormFromClient(Form):
    py_requires='gnrcomponents/framegrid:BagGrid'
    def th_form(self,form):
        tc = form.center.tabContainer()
        self.main_instancetab(tc.borderContainer(title='Info'))
        for pkgname, handler in [(c.split('_')[1], getattr(self, c)) for c in dir(self) if
                                 c.startswith('hostedinstance_')]:
            handler(tc.contentPane(datapath='.hosted_data.%s' % pkgname, title=self.db.packages[pkgname].name_long,
                                   nodeId='hosted_instance_data_%s' % pkgname,
                                   sqlContextName='sql_record_hosted_instance_%s' % pkgname,
                                   sqlContextRoot='instances.dlg.record.hosted_data.%s' % pkgname))

    def main_instancetab(self, bc):
        pane = bc.contentPane(region='top')
        pane.div('!!Manage instances', _class='pbl_roundedGroupLabel')
        fb = pane.formbuilder(cols=1, border_spacing='6px')
        fb.field('code', width='15em', lbl='!!Instance Name')
        pane.dataRpc('.$creation_result', 'createInst', instance_code='=.code', instance_exists='=.$instance_exists',
                     site_exists='=.$site_exists',
                     _fired='^.$create', _onResult='FIRE .$created', _userChanges=True)
        pane.dataController("""
                if (site_path){
                SET .site_path=site_path;
                SET .$site_exists=true;
                }
                if (instance_path){
                SET .path=instance_path;
                SET .$instance_exists=true;
                }
                """, site_path='=.$creation_result.site_path',
                            instance_path='=.$creation_result.instance_path',
                            _fired='^.$created', _userChanges=True)

        def struct(struct):
            r = struct.view().rows()
            r.cell('type', name='Slot type', width='15em',edit=dict(dbtable='hosting.slot_type',
                            columns='$code,$description', rowcaption='$code',
                            exclude=True, hasDownArrow=True))
            r.cell('qty', name='Qty', width='4em', dtype='I',edit=True)
            return struct

        bc.contentPane(region='center').bagGrid(title='!!Slot configuration',
                                  storepath='#FORM.record.slot_configuration', struct=struct,
                                  datapath='#FORM.confGrid',
                                autoWidth=True,
                                  add_action=True, del_action=True)


    @public_method
    def th_onLoading(self, record, newrecord, loadingParameters, recInfo):
        instance_exists = self.db.packages['hosting'].instance_exists(record['code'])
        site_exists = self.db.packages['hosting'].site_exists(record['code'])
        record.setItem('$instance_exists', instance_exists)
        record.setItem('$site_exists', site_exists)


    def th_options(self):
        return dict(dialog_height='400px', dialog_width='600px')
