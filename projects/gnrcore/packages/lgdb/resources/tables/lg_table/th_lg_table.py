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
        top.slotToolbar('5,sections@lg_pkg,*,sections@groups,5',
                       childname='superiore',
                       sections_groups_remote=self.sectionGroups,
                       _position='<bar',gradient_from='#999',gradient_to='#666')

    @public_method
    def sectionGroups(self):
        groups= self.db.table('lgdb.lg_table').query('$group',distinct=True, 
                                                where= '$group IS NOT NULL').fetch()
        
        result=[]
        result.append(dict(code='all', caption='All'))
        for g in groups:
            result.append(dict(code=g['group'], caption=g['group'], condition='$group= :gr', condition_gr=g['group']))
        result.append(dict(code='no_group', caption='No group', condition='$group IS NULL'))
        return result


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
        fb = top.div(margin_right='10px').formbuilder(cols=2,
                                                      border_spacing='4px',
                                                      width='100%',
                                                      fld_width='100%',
                                                      colswidth='auto')
        fb.field('lg_pkg')
        fb.field('name')
        fb.field('group')
        fb.field('description', colspan=2)
        fb.field('multidb', colspan=2)
        fb.field('notes', tag='simpleTextArea',colspan=2, height='90px')
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
