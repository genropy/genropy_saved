#!/usr/bin/python
# -*- coding: UTF-8 -*-

from gnr.web.gnrbaseclasses import BaseComponent
from gnr.core.gnrdecorator import public_method

class View(BaseComponent):

    def th_struct(self,struct):
        r = struct.view().rows()
        r.fieldcell('title')
        r.fieldcell('letterhead_id')

    def th_order(self):
        return 'title'

    def th_query(self):
        return dict(column='title', op='contains', val='')



class Form(BaseComponent):

    def th_form(self, form):
        bc = form.center.borderContainer()
        fb = bc.contentPane(region='top',datapath='.record').formbuilder(cols=2, border_spacing='4px')
        fb.field('title')
        fb.field('confirm_label',width='20em')
        fb.field('tag_rule',width='20em')
        fb.field('all_users',width='20em',html_label=True)
        fb.field('letterhead_id')
        sc = bc.stackContainer(region='center')

        self.templatePage(sc.framePane(title='!!Template'))
        self.connectedUser(sc.contentPane(title='!!Users'))

    def templatePage(self,frame):
        centerpane = frame.center.contentPane(overflow='auto')
        centerpane.dataRecord('#FORM.sample_letterhead','adm.htmltemplate',pkey='^#FORM.record.letterhead_id',
                                _if='pkey',_else='return new gnr.GnrBag();')

        centerpane.dataFormula('#FORM.available_height','(center_height || 297)+"mm";',center_height='^#FORM.sample_letterhead.center_height')
        centerpane.dataFormula('#FORM.available_width','(center_width || 210)+"mm";',center_width='^#FORM.sample_letterhead.center_width')
        paper = centerpane.div(height='^#FORM.available_height',width='^#FORM.available_width',margin='10px',border='1px dotted silver')
        bar = frame.top.slotToolbar('5,parentStackButtons,*,selector,5')
        fb = bar.selector.formbuilder(cols=1, border_spacing='0')

        fb.dbSelect(dbtable='adm.user',value='^#FORM.testuser.pkey',lbl='Test User',#condition='$tipo_id=:t_id',
                    condition_t_id='^#FORM.pkey')
        rpc = fb.dataRecord('#FORM.testuser.record','adm.user',
                            pkey='==_pkey || "*newrecord*"',
                            _pkey='^#FORM.testuser.pkey',
                            ignoreMissing=True)

        paper.templateChunk(template='^#FORM.record.template',table='adm.user',editable=True,dataProvider=rpc,
                            datasource='^#FORM.testuser.record',
                            showLetterhead='^#FORM.sample_letterhead.id',
                            constrain_height='^#FORM.available_height',
                            constrain_width='^#FORM.available_width',
                            constrain_border='1px solid silver',
                            constrain_shadow='3px 3px 5px gray',
                            constrain_margin='4px',
                            constrain_rounded=3,
                            selfsubscribe_onChunkEdit='this.form.save();')
    @public_method
    def getSampleLetterhead(self,letterhead_id=None):
        pass

    def connectedUser(self,pane):
        th = pane.plainTableHandler(relation='@notification_users',viewResource='ViewFromNotification',delrow=True,picker='user_id')
        th.view.top.bar.replaceSlots('vtitle','parentStackButtons')


    def th_options(self):
        return dict(dialog_height='400px', dialog_width='600px')
