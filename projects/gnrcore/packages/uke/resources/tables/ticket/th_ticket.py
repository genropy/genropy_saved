#!/usr/bin/python3
# -*- coding: utf-8 -*-

from gnr.web.gnrbaseclasses import BaseComponent
from gnr.core.gnrdecorator import public_method

class View(BaseComponent):

    def th_struct(self,struct):
        r = struct.view().rows()
        r.fieldcell('subject')
        r.fieldcell('ticket_type_code')
        r.fieldcell('summary')
        r.fieldcell('description')
        r.fieldcell('table_identifier')

    def th_order(self):
        return 'subject'

    def th_query(self):
        return dict(column='subject', op='contains', val='')


class ViewFromPkgTable(BaseComponent):

    def th_struct(self,struct):
        r = struct.view().rows()
        r.fieldcell('subject')
        r.fieldcell('ticket_type_code')
        r.fieldcell('summary')
        r.fieldcell('description')

    def th_order(self):
        return 'subject'

    def th_query(self):
        return dict(column='subject', op='contains', val='')


class Form(BaseComponent):
    py_requires = """gnrcomponents/attachmanager/attachmanager:AttachManager""" 

    def th_form(self, form):
        bc = form.center.borderContainer()
        self.ticket_head(bc.contentPane(region='top',datapath='.record'))
        tc = bc.tabContainer(region='center')
        self.ticket_description(tc.contentPane(title='!!Description'))
        self.ticket_people(tc.contentPane(title='!!People'))
        self.ticket_attachments(tc.contentPane(title='!!Attachments'))

    def ticket_description(self,pane):
        pane.simpleTextArea(value='^.description',editor=True)

    def ticket_people(self,pane):
        pane.inlineTableHandler(relation='@ticket_person',picker='person_id',pbl_classes=True,margin='2px',
                                viewResource='ViewFromTicket')

    def ticket_attachments(self,pane):
        pane.attachmentGrid(screenshot=True)

    def ticket_head(self,pane):
        fb = pane.div(margin_right='30px').formbuilder(cols=2, border_spacing='4px',colswidth='auto',fld_width='100%')
        fb.field('subject',colspan=2)
        fb.field('table_identifier')
        fb.field('ticket_type_code')
        fb.field('summary',colspan=2,tag='simpleTextArea')


    def th_options(self):
        return dict(dialog_height='400px', dialog_width='600px')

class FormExternal(Form):
    py_requires = """gnrcomponents/attachmanager/attachmanager:AttachManager,gnrcomponents/filepicker:FilePicker""" 

    def ticket_head(self,pane):
        fb = pane.div(margin_right='30px').formbuilder(cols=2, border_spacing='4px',colswidth='auto',fld_width='100%')
        fb.field('subject',colspan=2)
        fb.field('ticket_type_code',colspan=2)
        fb.field('summary',colspan=2,tag='simpleTextArea')

    def th_options(self):
        return dict(dialog_height='400px', dialog_width='600px')


class FormFromPkgTable(Form):

    def ticket_head(self,pane):
        fb = pane.div(margin_right='30px').formbuilder(cols=2, border_spacing='4px',colswidth='auto',fld_width='100%')
        fb.field('subject')
        fb.field('ticket_type_code')
        fb.field('summary',colspan=2,tag='simpleTextArea')

    def th_options(self):
        return dict(dialog_height='400px', dialog_width='600px')
