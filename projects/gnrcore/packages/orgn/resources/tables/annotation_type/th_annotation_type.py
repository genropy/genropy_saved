#!/usr/bin/python
# -*- coding: UTF-8 -*-

from gnr.web.gnrbaseclasses import BaseComponent
from gnr.core.gnrdecorator import public_method

class View(BaseComponent):

    def th_struct(self,struct):
        r = struct.view().rows()
        r.fieldcell('description')
        r.fieldcell('code')
        r.fieldcell('restrictions')

    def th_order(self):
        return 'description'

    def th_query(self):
        return dict(column='description', op='contains', val='')



class Form(BaseComponent):
    py_requires='gnrcomponents/dynamicform/dynamicform:DynamicForm'

    def th_form(self, form):
        bc = form.center.borderContainer()
        top = bc.contentPane(region='top',datapath='.record')
        fb = top.formbuilder(cols=1, border_spacing='4px')
        fb.field('code')
        fb.field('description')
        restrictions = self.db.table('orgn.annotation').getRestrictions()
        if restrictions:
            fb.field('restrictions',tag='checkBoxText',values=restrictions,popup=True,cols=1)
        tc = bc.tabContainer(region='center',margin='2px')
        self.defaultActions(tc.contentPane(title='!!Default actions'))
        tc.contentPane(title='!!Custom fields').fieldsGrid(title='Fields',pbl_classes=True,margin='2px')


    def defaultActions(self,pane):
        pane.plainTableHandler(relation='@default_actions',viewResource='ViewFromAnnotationType',
                                picker='action_type_id',
                                picker_condition="""(CASE WHEN $restrictions IS NOT NULL AND :restriction IS NOT NULL 
                                                          THEN string_to_array(:restriction,',') && string_to_array($restrictions,',') 
                                                    ELSE TRUE END)""",
                                picker_condition_restriction='^#FORM.record.restrictions',
                                delrow=True,margin='2px')

    def th_options(self):
        return dict(dialog_height='400px', dialog_width='600px')
