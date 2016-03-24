#!/usr/bin/python
# -*- coding: UTF-8 -*-

from gnr.web.gnrbaseclasses import BaseComponent
from gnr.core.gnrdecorator import public_method,metadata

class View(BaseComponent):

    def th_struct(self,struct):
        r = struct.view().rows()
        r.fieldcell('code',width='5em')
        r.fieldcell('description',width='20em')
        r.fieldcell('extended_description',width='20em')
        r.fieldcell('restrictions',width='20em')
        r.fieldcell('deadline_days',width='5em')
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
        topbc = bc.borderContainer(region='top',datapath='.record',height='200px')

        topleft = topbc.roundedGroup(title='!!Action type info',region='left',width='700px')
        fb = topleft.div(margin_right='15px').formbuilder(cols=3, border_spacing='4px',width='100%',colswidth='auto',fld_width='100%')
        fb.field('code',width='5em')
        fb.field('description',colspan=2)
        fb.field('deadline_days',width='6em')
        fb.field('default_priority',width='10em')
        fb.field('default_tag',condition='$child_count = 0 AND $isreserved IS NOT TRUE',
                tag='dbselect',
                dbtable='adm.htag',alternatePkey='code',hasDownArrow=True)
        restrictions = self.db.table('orgn.annotation').getLinkedEntities()
        if restrictions:
            fb.field('restrictions',tag='checkBoxText',values=restrictions,popup=True,cols=1,colspan=3,width='100%')
        fb.field('extended_description',tag='simpleTextArea',lbl='!!Extended description',colspan=3,width='100%')
        fb.div(height='17px',width='4em',lbl='Background',
               border='1px solid gray',
               cursor='pointer',background='^.background_color').menu(modifiers='*',_class='colorPaletteMenu').menuItem().colorPalette(value='^.background_color')
        fb.div(height='17px',width='4em',lbl='Text',
               border='1px solid gray',
               cursor='pointer',background='^.color').menu(modifiers='*',_class='colorPaletteMenu').menuItem().colorPalette(value='^.color')

        topright = topbc.roundedGroupFrame(title='!!Text template',region='center'
                            ).center.contentPane(overflow='hidden')
        topright.simpleTextArea(value='^.text_template',position='absolute',top=0,left=0,right=0,bottom=0,border=0)
        tc = bc.tabContainer(region='center',margin='2px')
        tc.contentPane(title='!!Outcomes',datapath='#FORM').inlineTableHandler(relation='@outcomes',addrow=False,
                                                                           picker='outcome_action_type_id',
                                                                           picker_condition="""(CASE WHEN $restrictions IS NOT NULL AND :restriction IS NOT NULL 
                                                                                    THEN  string_to_array($restrictions,',') @> string_to_array(:restriction,',')
                                                                                ELSE TRUE END)""",
                                picker_condition_restriction='^#FORM.record.restrictions',
                                pbl_classes=True,searchOn=False,configurable=False,viewResource='ViewFromActionType')
        tc.contentPane(title='!!Action fields').fieldsGrid(title='!!Fields',pbl_classes=True,margin='2px')
        self.fullTemplate(tc.contentPane(title='!!Full template'))

    def fullTemplate(self,pane):
        rpc = pane.dataRecord('#FORM.sample_annotation.record','orgn.annotation',
                            pkey='"*newrecord*"',ignoreMissing=True,
                            default_action_type_id='^#FORM.pkey')
        paper = pane.div(height='297mm',width='210mm',margin='10px',border='1px dotted silver')
        paper.templateChunk(template='^#FORM.record.full_template',
                            table='orgn.annotation',editable=True,
                            dataProvider=rpc,
                            datasource='^#FORM.sample_annotation.record',
                            selfsubscribe_onChunkEdit='this.form.save();')


    def th_options(self):
        return dict(dialog_height='400px', dialog_width='600px')
