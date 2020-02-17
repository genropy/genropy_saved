#!/usr/bin/python3
# -*- coding: utf-8 -*-

from gnr.web.gnrbaseclasses import BaseComponent
from gnr.core.gnrdecorator import public_method

class View(BaseComponent):

    def th_struct(self,struct):
        r = struct.view().rows()
        r.fieldcell('lg_pkg')
        r.fieldcell('name')
        r.fieldcell('sqlname')
        r.fieldcell('description')
        r.fieldcell('notes')
        r.fieldcell('group')
        r.fieldcell('multidb')

    def th_order(self):
        return 'lg_pkg'

    def th_query(self):
        return dict(column='name', op='contains', val='')

    def th_top_sup(self,top):
        top.slotToolbar('*,sections@lg_pkg,*',
                       childname='superiore',
                       _position='<bar',gradient_from='#999',gradient_to='#666')

class ViewFromPackage(BaseComponent):
    
    def th_struct(self,struct):
        r = struct.view().rows()
        r.fieldcell('name')
        r.fieldcell('sqlname')
        r.fieldcell('description')
        r.fieldcell('notes')
        r.fieldcell('group')
        r.fieldcell('multidb')

    def th_order(self):
        return 'lg_pkg'



class Form(BaseComponent):

    def th_form(self, form):
        bc = form.center.borderContainer()
        top = bc.contentPane(region='top',datapath='.record')
        fb = top.formbuilder(cols=2, border_spacing='4px')
        fb.field('lg_pkg')
        fb.field('name')
        fb.field('description')
        fb.field('notes')
        fb.field('group')
        fb.field('multidb')
        tc = bc.tabContainer(region='center')

        tc.contentPane(title='Columns').inlineTableHandler(relation='@columns')

        tc.contentPane(title='Outgoing Relations').plainTableHandler(table='lgdb.lg_relation',
                                                            nodeId='outgoing_relations',
                                                            datapath='outgoing_relations',
                                                            condition='@relation_column.lg_table_id=:tbl_id',
                                                            condition_tbl_id='^#FORM.pkey')

        tc.contentPane(title='Incoming Relations').plainTableHandler(table='lgdb.lg_relation',
                                                            nodeId='incoming_relations',
                                                            datapath='incoming_relations',
                                                            condition='@related_column.lg_table_id=:tbl_id',
                                                            condition_tbl_id='^#FORM.pkey')


    def th_options(self):
        return dict(dialog_height='600px', dialog_width='800px' )
