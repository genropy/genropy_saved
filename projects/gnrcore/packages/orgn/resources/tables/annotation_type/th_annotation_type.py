#!/usr/bin/python
# -*- coding: utf-8 -*-

from gnr.web.gnrbaseclasses import BaseComponent
from gnr.core.gnrdecorator import public_method,metadata

class View(BaseComponent):

    def th_struct(self,struct):
        r = struct.view().rows()
        r.fieldcell('description')
        r.fieldcell('code')
        r.fieldcell('restrictions')
        r.fieldcell('color',name='Color',width='7em',
                    _customGetter="""function(row){
                        return dataTemplate("<div style='background:$background_color;color:$color;border:1px solid $color;text-align:center;border-radius:10px;'>Sample</div>",row)
                    }""")
        r.fieldcell('background_color',hidden=True)

    def th_order(self):
        return 'description'

    def th_query(self):
        return dict(column='description', op='contains', val='')

    def th_top_custom(self,top):
        restrictions = self.db.table('orgn.annotation').getLinkedEntities()
        if restrictions:
            top.bar.replaceSlots('searchOn','searchOn,sections@typerestrictions')

    @metadata(multiButton=True)
    def th_sections_typerestrictions(self):
        restrictions = self.db.table('orgn.annotation').getLinkedEntities()
        condition = """(CASE WHEN $restrictions IS NULL THEN TRUE
                             ELSE string_to_array(:restriction,',') && string_to_array($restrictions,',') 
                        END)"""
        result = [dict(code='all',caption='!!All')]
        for r in restrictions.split(','):
            code,description = r.split(':')
            result.append(dict(code=code,caption=description,condition=condition,condition_restriction=code))
        return result

    def th_options(self):
        return dict(virtualStore=False)



class Form(BaseComponent):
    py_requires='gnrcomponents/dynamicform/dynamicform:DynamicForm'

    def th_form(self, form):
        bc = form.center.borderContainer()
        topbc = bc.borderContainer(region='top',height='200px')
        topleft = topbc.roundedGroup(title='!!Type info',region='left',datapath='.record',width='500px')
        self.defaultActions(topbc.contentPane(region='center'))

        fb = topleft.formbuilder(cols=2, border_spacing='4px')
        fb.field('code',width='5em')
        fb.field('description',width='20em')
        restrictions = self.db.table('orgn.annotation').getLinkedEntities()
        if restrictions:
            fb.field('restrictions',tag='checkBoxText',values=restrictions,popup=True,cols=1,colspan=2,width='100%')
        fb.div(height='17px',width='4em',lbl='Background',
               border='1px solid gray',
               cursor='pointer',background='^.background_color').menu(modifiers='*',_class='colorPaletteMenu').menuItem().colorPalette(value='^.background_color')
        fb.div(height='17px',width='4em',lbl='Text',
               border='1px solid gray',
               cursor='pointer',background='^.color').menu(modifiers='*',_class='colorPaletteMenu').menuItem().colorPalette(value='^.color')

        bc.contentPane(region='center',margin='2px').fieldsGrid(title='Fields',pbl_classes=True,margin='2px')

    def defaultActions(self,pane):
        pane.plainTableHandler(relation='@default_actions',viewResource='ViewFromAnnotationType',
                                picker='action_type_id',
                                picker_condition="""(CASE WHEN $restrictions IS NOT NULL AND :restriction IS NOT NULL 
                                                          THEN  string_to_array($restrictions,',') @> string_to_array(:restriction,',')
                                                    ELSE TRUE END)""",
                                picker_condition_restriction='^#FORM.record.restrictions',
                                delrow=True,margin='2px',pbl_classes=True,configurable=False)

    def th_options(self):
        return dict(dialog_height='400px', dialog_width='600px')
