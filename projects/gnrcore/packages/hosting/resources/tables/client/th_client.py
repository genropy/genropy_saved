#!/usr/bin/python
# -*- coding: UTF-8 -*-

from gnr.web.gnrbaseclasses import BaseComponent
from gnr.core.gnrdecorator import public_method
from gnr.core.gnrbag import Bag

class View(BaseComponent):

    def th_struct(self,struct):
        r = struct.view().rows()
        r.fieldcell('code')
        r.fieldcell('user_id')
        r.fieldcell('hosted_data')

    def th_order(self):
        return 'code'

    def th_query(self):
        return dict(column='code', op='contains', val='')

class Form(BaseComponent):
    py_requires='hosted:HostedClient'

    def th_form(self, form):
        bc = form.center.borderContainer()
        top = bc.borderContainer(region='top', height='140px',datapath='.record')
        right = top.contentPane(region='right', width='350px')
        self.hosted_card_linker(right)
        center = top.roundedGroup(title='!!Client hosting',region='center')
        fb = center.formbuilder(cols=1, border_spacing='3px', fld_width='100%',
                                width='350px')
        fb.field('code')
        fb.field('user_id')

        tc = bc.tabContainer(region='center',margin='2px')
        self.main_clienttab(tc.contentPane(title='Info',datapath='#FORM'))
        for pkgname, handler in [(c.split('_')[1], getattr(self, c)) for c in dir(self) if
                                 c.startswith('hostedclient_')]:
            handler(tc.contentPane(datapath='#FORM.record.hosted_data.%s' % pkgname,
                                   title=self.db.packages[pkgname].name_long))


    def main_clienttab(self, pane):
        pane.dialogTableHandler(relation='@instances',formResource='FormFromClient',title='Instances',margin='2px',pbl_classes=True)
       
    @public_method
    def createInst(self, instance_code=None, instance_exists=None, site_exists=None):
        result = Bag()
        instancetbl = self.db.table('hosting.instance')
        if not instance_exists:
            result['instance_path'] = instancetbl.create_instance(instance_code, self.site.instance_path,
                                                                  self.site.gnrapp.config)
        if not site_exists:
            result['site_path'] = instancetbl.create_site(instance_code, self.site.site_path, self.site.config)
        return result

    def th_options(self):
        return dict(dialog_height='400px', dialog_width='600px')
