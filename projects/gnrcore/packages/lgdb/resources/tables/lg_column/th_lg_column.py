#!/usr/bin/python3
# -*- coding: utf-8 -*-

from gnr.web.gnrbaseclasses import BaseComponent
from gnr.core.gnrdecorator import public_method

class View(BaseComponent):

    def th_struct(self,struct):
        r = struct.view().rows()
        r.fieldcell('lg_table_id')
        r.fieldcell('name', width='8em')
        r.fieldcell('data_type', name='T', width='3em')
        r.fieldcell('old_type', name='OT', width='3em')
        r.fieldcell('description', width='15em', edit=True)
        r.fieldcell('notes', width='40em', edit=dict(tag='simpleTextArea', height='80px'))
        r.fieldcell('group', width='8em', edit=True)

    def th_order(self):
        return 'lg_table_id'

    def th_query(self):
        return dict(column='name', op='contains', val='')

    def th_queryBySample(self):
        return dict(fields=[dict(field='@lg_table_id.sqlname', lbl='Table', width='12em'),
                            dict(field='name', lbl='Name', width='12em'),
                            dict(field='description', lbl='Description', width='14em'),
                            dict(field='notes', lbl='Notes', width='14em')],
                    cols=4, 
                    isDefault=True)

    def th_top_sup(self,top):
        top.slotToolbar('*,sections@types,*',
                       childname='superiore',
                       sections_types_remote=self.sectionTypes,
                       _position='<bar',gradient_from='#999',gradient_to='#666')

    @public_method
    def sectionTypes(self):
        types = self.db.table('lgdb.lg_column').query('$data_type', distinct=True, 
                                                where= '$data_type IS NOT NULL').fetch()

        result=[]
        result.append(dict(code='all', caption='All'))
        for t in types:
            result.append(dict(code=t['data_type'], caption=t['data_type'], condition='$data_type= :tp', condition_tp=t['data_type']))
        result.append(dict(code='no_type', caption='No type', condition='$data_type IS NULL'))
        return result


class Form(BaseComponent):

    def th_form(self, form):
        pane = form.record
        fb = pane.div(margin_right='10px').formbuilder(cols=2, border_spacing='4px', width='100%', fld_width='100%')
        fb.field('lg_table_id', readOnly=True, background='rgba(128, 128, 128, 0.125)' )
        fb.field('name', readOnly=True, background='rgba(128, 128, 128, 0.125)' )
        fb.field('data_type', readOnly=True, background='rgba(128, 128, 128, 0.125)' )
        fb.field('old_type')
        fb.field('group')
        fb.field('description', colspan=2, readOnly=True, background='rgba(128, 128, 128, 0.125)' )
        fb.field('notes', tag='simpleTextArea', height='90px')

    def th_options(self):
        return dict(dialog_height='400px', dialog_width='600px' )
