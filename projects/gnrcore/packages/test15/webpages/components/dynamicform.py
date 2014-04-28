# -*- coding: UTF-8 -*-
#--------------------------------------------------------------------------
# Copyright (c) : 2004 - 2007 Softwell sas - Milano 
# Written by    : Giovanni Porcari, Michele Bertoldi
#                 Saverio Porcari, Francesco Porcari , Francesco Cavazzana
#--------------------------------------------------------------------------
#This library is free software; you can redistribute it and/or
#modify it under the terms of the GNU Lesser General Public
#License as published by the Free Software Foundation; either
#version 2.1 of the License, or (at your option) any later version.

#This library is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
#Lesser General Public License for more details.

#You should have received a copy of the GNU Lesser General Public
#License along with this library; if not, write to the Free Software
#Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA

"""
Component for thermo:
"""
from gnr.web.gnrbaseclasses import BaseComponent
from gnr.core.gnrbag import Bag
from gnr.core.gnrstring import asDict
from gnr.core.gnrdecorator import public_method,customizable
from gnr.core.gnrdict import dictExtract
from gnr.web.gnrwebstruct import struct_method

AUTOWDG = {'T':'TextBox','L':'NumberTextBox','D':'DateTextbox','R':'NumberTextBox','N':'NumberTextBox','H':'TimeTextBox','B':'CheckBox'};


class Form(BaseComponent):
    css_requires='gnrcomponents/dynamicform/dynamicform'
    js_requires='gnrcomponents/dynamicform/dynamicform'

    def th_form(self,form):
        bc = form.center.borderContainer(datapath='.record')
        bottom = bc.contentPane(region='bottom',border_top='1px solid silver')
        pane = bc.contentPane(region='center')
        box = pane.div(_class='^#FORM.boxClass',margin='5px',margin_top='10px',margin_right='15px')
        fb = box.formbuilder(cols=3, border_spacing='4px',tdl_width='5em',width='100%')
        #tbl = pane.getInheritedAttributes()['table']
        fb.field('code',validate_notnull=True,validate_notnull_error='!!Required',width='8em', 
                validate_regex='![^A-Za-z0-9_]', 
                validate_regex_error='!!Invalid code: "." char is not allowed',#validate_case='l',
                validate_nodup=True,validate_nodup_error='!!Already existing code',
                validate_nodup_condition='$maintable_id=:fkey',validate_nodup_fkey='=#FORM.record.maintable_id',
                validate_case='l',
                ghost='!!Field code')
        fb.field('description',validate_notnull=True,validate_notnull_error='!!Required',width='100%',colspan=2,
                    ghost='!!Field description')

        fb.field('data_type',values='!!T:Text,L:Integer,N:Decimal,D:Date,B:Boolean,H:Time,P:Image',width='8em',tag='FilteringSelect')
        fb.dataController("dynamicFormHandler.onDataTypeChange(this,data_type,_reason,this.form.isNewRecord());",data_type="^.data_type")

        fb.field('calculated',lbl='',label='!!Calculated')
        fb.dataController("dynamicFormHandler.onSetCalculated(this,calculated);",calculated="^.calculated")

        fb.br()
        
        fb.field('formula',colspan=3,width='100%',row_class='df_row field_calculated',lbl_vertical_align='top',height='60px',tag='simpleTextArea')
        
        fb.field('wdg_tag',values='^#FORM.allowedWidget',tag='filteringSelect',
                    row_class='df_row field_enterable',colspan=2)
        fb.br()
        fb.dataController("dynamicFormHandler.onSetWdgTag(this,wdg_tag);",wdg_tag="^.wdg_tag")
        
        fb.numberTextBox(value='^.wdg_kwargs.colspan',lbl='!!Colspan', row_class='df_row field_enterable field_calculated',width='100%')
        fb.textbox(value='^.wdg_kwargs.width',lbl='!!Width', row_class='df_row field_enterable field_calculated',width='100%')
        fb.textbox(value='^.wdg_kwargs.height',lbl='!!Height', row_class='df_row field_enterable field_calculated',width='100%')
        fb.checkbox(value='^.wdg_kwargs.keepable',label='!!Keepable value', row_class='df_row field_enterable')
        fb.checkbox(value='^.wdg_kwargs.speech',label='!!Vocal input', row_class='df_row field_enterable')
        fb.br()
        fb.checkbox(value='^.wdg_kwargs.editor',label='!!Full text editor', row_class='df_row field_simpletextarea')
        fb.br()

        
        fb.field('source_filteringselect',colspan=3,row_class='df_row field_filteringselect',
                tag='simpleTextArea',width='100%',lbl_vertical_align='top',height='60px',
                ghost='!!c1:description1\n c2:description2')
        fb.field('source_combobox',colspan=3,row_class='df_row field_combobox',
                tag='simpleTextArea',width='100%',lbl_vertical_align='top',height='60px',
                 ghost='!!description1\n description2')
        fb.field('source_checkboxtext',colspan=3,row_class='df_row field_checkboxtext field_checkboxtext_nopopup',
                tag='simpleTextArea',width='100%',lbl_vertical_align='top',height='60px',
                ghost='!!description1\n description2')
        fb.field('source_dbselect',colspan=3,row_class='df_row field_dbselect',width='100%',ghost='!!pkg.table')  
        
        
        fb.field('validate_case',row_class='df_row field_textbox',width='100%')
        fb.br()
        
        fb.field('validate_range',width='100%',row_class='df_row field_numbertextbox field_numberspinner field_currencytextbox field_horizontalslider',ghost='min:max')
        fb.field('standard_range',width='100%',row_class='df_row field_numbertextbox field_numberspinner field_currencytextbox field_horizontalslider',ghost='min:max')
        fb.br()
        fb.numbertextBox(value='^.wdg_kwargs.crop_height',width='100%',row_class='df_row field_img',lbl='!!Crop H')
        fb.numbertextBox(value='^.wdg_kwargs.crop_width',width='100%',row_class='df_row field_img',lbl='!!Crop W')
        fb.br()
        
        footer = bottom.div(margin='5px',margin_right='15px').formbuilder(cols=2, border_spacing='4px',width='100%',fld_width='18em')
        footer.field('mandatory',lbl='',label='!!Mandatory',row_hidden='^.calculated')
        footer.field('default_value',lbl='Dflt.Value')
        footer.field('field_format',values='^#FORM.allowedFormat',tag='Combobox',lbl_width='4em')
        footer.field('field_placeholder',lbl_width='6em')
        footer.field('field_visible',lbl_vertical_align='top',height='60px',tag='simpleTextArea')
        footer.field('field_style',lbl_vertical_align='top',height='60px',tag='simpleTextArea')
        footer.field('field_tip',lbl_vertical_align='top',height='60px',tag='simpleTextArea')
        footer.field('field_mask',lbl_vertical_align='top',height='60px',tag='simpleTextArea')
    

    def th_options(self):
        return dict(dialog_height='450px',dialog_width='600px')



class View(BaseComponent):
    def th_struct(self,struct):
        r = struct.view().rows()
        r.fieldcell('_row_count',counter=True,hidden=True)
        r.fieldcell('code', name='!!Code', width='5em',draggable=True)
        r.fieldcell('description', name='!!Description', width='15em')
        r.fieldcell('data_type', name='!!Type', width='10em')
        r.fieldcell('wdg_tag',name='!!Widget',width='10em')
        r.fieldcell('mandatory', name='!!Mandatory',width='7em')
    
    def th_order(self):
        return '_row_count'

class DynamicFormBagManager(BaseComponent):

    def df_fieldsBagStruct(self,struct):
        r = struct.view().rows()
        r.cell('code', name='!!Code', width='5em')
        r.cell('description', name='!!Description', width='15em')
        r.cell('data_type', name='!!Type', width='10em')
        r.cell('wdg_tag',name='!!Widget',width='10em')
        r.cell('page',name='!!Page',width='10em')
        r.cell('mandatory', name='!!Mandatory',width='7em')

    @customizable
    def df_fieldsBagForm(self,form):
        form.top.slotToolbar('2,navigation,*,delete,add,save,semaphore,locker,2')
        form.dataController('SET #FORM.ftitle = desc || newfield;',desc='=#FORM.record.description',newfield='!!New Field',_fired='^#FORM.controller.loaded')
        bc = form.center.borderContainer(datapath='.record')
        pane = bc.contentPane(region='center')
        self.df_customTabs(bc.tabContainer(region='bottom',height='160px',margin='2px'))
        box = pane.div(_class='^#FORM.boxClass',margin='5px',margin_top='10px',margin_right='15px')
        fb = box.formbuilder(cols=3, border_spacing='4px',tdl_width='5em',width='100%')
        #tbl = pane.getInheritedAttributes()['table']
        fb.textbox(value='^.code',validate_notnull=True,validate_notnull_error='!!Required',width='8em', 
                validate_regex='![^A-Za-z0-9_]', 
                validate_regex_error='!!Invalid code: "." char is not allowed',#validate_case='l',
                validate_case='l',lbl='!!Code',
                ghost='!!Field code')
        fb.textbox(value='^.description',validate_notnull=True,validate_notnull_error='!!Required',width='100%',colspan=2,
                    ghost='!!Field description',lbl='!!Description')
        fb.filteringSelect(value='^.data_type',values='!!T:Text,L:Integer,N:Decimal,D:Date,B:Boolean,H:Time,P:Image,GR:Graph',width='8em',lbl='!!Type')
        fb.dataController("dynamicFormHandler.onDataTypeChange(this,data_type,_reason,this.form.isNewRecord());",data_type="^.data_type")

        fb.checkbox(value='^.calculated',lbl='',label='!!Calculated')
        fb.dataController("dynamicFormHandler.onSetCalculated(this,calculated);",calculated="^.calculated")

        fb.textbox(value='^.page',lbl='Page')
        self.df_formulaField(fb)        
        fb.filteringSelect(value='^.wdg_tag',lbl='!!Widget',values='^#FORM.allowedWidget',row_class='df_row field_enterable',colspan=2)
        fb.br()
        fb.dataController("dynamicFormHandler.onSetWdgTag(this,wdg_tag);",wdg_tag="^.wdg_tag")
        
        fb.numberTextBox(value='^.wdg_kwargs.colspan',lbl='!!Colspan', row_class='df_row field_enterable field_calculated',width='100%')
        fb.textbox(value='^.wdg_kwargs.width',lbl='!!Width', row_class='df_row field_enterable field_calculated',width='100%')
        fb.textbox(value='^.wdg_kwargs.height',lbl='!!Height', row_class='df_row field_enterable field_calculated',width='100%')
        fb.checkbox(value='^.wdg_kwargs.keepable',label='!!Keepable value', row_class='df_row field_enterable')
        fb.checkbox(value='^.wdg_kwargs.speech',label='!!Vocal input', row_class='df_row field_enterable')
        fb.br()
        fb.checkbox(value='^.wdg_kwargs.editor',label='!!Full text editor', row_class='df_row field_simpletextarea')
        fb.br()
        fb.simpleTextArea(value='^.source_filteringselect',lbl='!!Source',colspan=3,row_class='df_row field_filteringselect',
                width='100%',lbl_vertical_align='top',height='60px',
                ghost='!!c1:description1\n c2:description2')
        fb.simpleTextArea(value='^.source_combobox',lbl='!!Source',colspan=3,row_class='df_row field_combobox',
                width='100%',lbl_vertical_align='top',height='60px',
                 ghost='!!description1\n description2')
        fb.simpleTextArea(value='^.source_checkboxtext',lbl='!!Source',colspan=3,row_class='df_row field_checkboxtext field_checkboxtext_nopopup',
                width='100%',lbl_vertical_align='top',height='60px',
                ghost='!!description1\n description2')
        fb.textbox(value='^.source_dbselect',lbl='!!Source',colspan=3,row_class='df_row field_dbselect',width='100%',ghost='!!pkg.table')  
        
        
        fb.filteringSelect(value='^.validate_case',lbl='!!Case',row_class='df_row field_textbox',width='100%',values='u:Uppercase,l:Lowercase,c:Capitalize,t:Title')
        fb.br()
        
        fb.textbox(value='^.validate_range',lbl='!!Range',width='100%',row_class='df_row field_numbertextbox field_numberspinner field_currencytextbox field_horizontalslider',ghost='min:max')
        fb.textbox(value='^.standard_range',lbl='!!Std.Range',width='100%',row_class='df_row field_numbertextbox field_numberspinner field_currencytextbox field_horizontalslider',ghost='min:max')
        fb.br()
        fb.numbertextBox(value='^.wdg_kwargs.crop_height',width='100%',row_class='df_row field_img',lbl='!!Crop H')
        fb.numbertextBox(value='^.wdg_kwargs.crop_width',width='100%',row_class='df_row field_img',lbl='!!Crop W')
        fb.br()
        fb.simpleTextArea(value='^.source_graph',lbl='!!Graph',colspan=3,row_class='df_row field_graph',
                width='100%',lbl_vertical_align='top',height='60px')
        return fb

    @customizable
    def df_formulaField(self,fb):
        return fb.simpleTextArea(value='^.formula',lbl='!!Formula',colspan=3,width='100%',row_class='df_row field_calculated',lbl_vertical_align='top',height='60px')


    @customizable
    def df_customTabs(self,tc):
        accesspane = tc.contentPane(title='!!Access')

        accesspane = accesspane.div(margin='5px',margin_right='15px').formbuilder(cols=2, border_spacing='4px',width='100%',fld_width='18em')

        accesspane.checkbox(value='^.mandatory',lbl='',label='!!Mandatory',row_hidden='^.calculated')
        accesspane.textbox(value='^.default_value',lbl='Dflt.Value')
        accesspane.simpleTextArea(value='^.field_visible',lbl='!!Visible if',lbl_vertical_align='top',height='60px')
        accesspane.simpleTextArea(value='^.field_tip',lbl='!!Tip',lbl_vertical_align='top',height='60px')
        accesspane.textbox(value='^.field_placeholder',lbl='!!Placeholder',lbl_width='6em')


        formatpane = tc.contentPane(title='!!Format and Mask')

        formatpane = formatpane.div(margin='5px',margin_right='15px').formbuilder(cols=2, border_spacing='4px',width='100%',fld_width='18em')
        formatpane.combobox(value='^.field_format',lbl='!!Format',values='^#FORM.allowedFormat',lbl_width='4em')
        formatpane.simpleTextArea(value='^.field_mask',lbl='!!Mask',lbl_vertical_align='top',height='60px')
    

        stylespane = tc.contentPane(title='!!Styles')

        stylespane = stylespane.div(margin='5px',margin_right='15px').formbuilder(cols=1, border_spacing='4px',width='100%')

        stylespane.simpleTextarea(value='^.field_style',title='!!Styles',height='100px',lbl='!!Styles',tdl_width='5em',width='100%')
        datagetter = tc.contentPane(title='!!Data getter',datapath='.getter')
        datagetter = datagetter.div(margin='5px',margin_right='15px').formbuilder(cols=2, border_spacing='4px',width='100%',fld_width='18em')
        datagetter.textbox(value='^.table',lbl='Table')
        datagetter.simpletextarea(value='^.where',lbl='Where',lbl_vertical_align='top',height='60px',rowspan=3,width='100%')
        datagetter.textbox(value='^.column',lbl='Column')
        datagetter.textbox(value='^.innerpath',lbl='Column')



class DynamicForm(BaseComponent):
    css_requires='gnrcomponents/dynamicform/dynamicform'
    js_requires='gnrcomponents/dynamicform/dynamicform'
    py_requires="""th/th:TableHandler,gnrcomponents/dynamicform/dynamicform:DynamicFormBagManager,
                    foundation/macrowidgets:RichTextEditor"""
    
    def __df_tpl_struct(self,struct):
        r = struct.view().rows()
        r.cell('tplname', name='Template', width='100%')
        
    def df_summaryTemplates(self,frame,table):
        bar = frame.top.slotToolbar('parentStackButtons,*,delgridrow,addrow_dlg')
        bc = frame.center.borderContainer(design='sidebar')
        left = bc.borderContainer(width='120px',region='left',splitter=True)
        fg = left.frameGrid(region='top',height='40%',margin_top='3px',splitter=True,storepath='#FORM.record.df_custom_templates',datamode='bag',
                 struct=self.__df_tpl_struct,grid_selectedLabel='.selectedLabel',grid_autoSelect=True,_class='noheader buttons_grid no_over')
        bar.addrow_dlg.slotButton('!!Add custom template',iconClass='iconbox add_row',
                                            action='genro.dlg.prompt(dlgtitle,{lbl:dlglbl,action:"FIRE #FORM.dynamicFormTester.newCustTpl=value;"},this);',
                                            dlgtitle='!!New template',dlglbl='!!Name')
        bar.delgridrow.slotButton('!!Delete selected template',iconClass='iconbox delete_row',
                                    action="""grid.publish("delrow");grid.widget.updateRowCount();""",grid=fg.grid)
        fg.dataController("""if(!currtemplates || currtemplates.len()==0){
            currtemplates = new gnr.GnrBag();
            currtemplates.setItem('base',new gnr.GnrBag({tpl:'',tplname:'base'}));
            SET #FORM.record.df_custom_templates = currtemplates;
        }
        """,currtemplates='=#FORM.record.df_custom_templates',_fired='^#FORM.controller.loaded')
        fg.dataController("""currtemplates.setItem(tplname,new gnr.GnrBag({tpl:'',tplname:tplname}));
                             setTimeout(function(){
                                grid.selection.select(grid.rowCount-1);
                             },1)
                                """,
                         tplname="^#FORM.dynamicFormTester.newCustTpl",
                          currtemplates='=#FORM.record.df_custom_templates',
                          grid=fg.grid.js_widget)
        fg.grid.dataFormula("#FORM.dynamicFormTester._editorDatapath", "'#FORM.record.df_custom_templates.'+selectedLabel;",
        selectedLabel="^.selectedLabel",_if='selectedLabel',_else='"#FORM.dynamicFormTester.dummypath"')
        frametree = left.framePane(region='center',margin_top='10px',margin_left='10px')
        frametree.top.div('!!Fields',font_size='.9em',font_weight='bold')
        treepane = frametree.center.contentPane().div(position='absolute',top='2px',bottom='2px',left='2px',right='4px',overflow='auto')
        treepane.tree(storepath='#FORM.dynamicFormTester.subfields',_fired='^#FORM.dynamicFormTester.subfields_tree',
                      _class='fieldsTree noIcon',hideValues=True,margin_top='6px',font_size='.9em',
                      labelAttribute='caption',draggable=True,onDrag='dragValues["text/plain"] = "$"+treeItem.attr.fieldpath;')
        treepane.dataRpc('#FORM.dynamicFormTester.subfields',self.db.table(table).df_subFieldsBag,
                        pkey='^#FORM.pkey',_fired='^#FORM.dynamicFormTester._refresh_fields',
                        _onResult='FIRE #FORM.dynamicFormTester.subfields_tree')
        center = bc.contentPane(region='center',datapath='^#FORM.dynamicFormTester._editorDatapath',margin_left='6px',margin='3px')
        self.RichTextEditor(center,value='^.tpl',toolbar='standard')
        
    @struct_method
    def df_fieldsGrid(self,pane,**kwargs):
        pane.attributes.update(overflow='hidden')
        bc = pane.borderContainer()
        mastertable = pane.getInheritedAttributes()['table']
        mastertblobj = self.db.table(mastertable)
        tc = bc.stackContainer(region='bottom',height='70%',splitter=True,hidden=True)
        self.df_previewForm(tc.framePane(title='!!Preview'),mastertable=mastertable)
        self.df_summaryTemplates(tc.framePane(title='!!Summary Templates'),mastertable)        
        center = bc.contentPane(region='center',overflow='hidden')
        if mastertblobj.column('df_fields') is None:
            th = self.df_fieldsTableGrid(center,**kwargs)
        else:
            th = self.df_fieldsBagGrid(center,mastertable=mastertable,**kwargs)
        bar = th.view.top.bar.replaceSlots('*,delrow','fbfields,showpreview,*,delrow')
        bar.showpreview.checkbox(value='^#FORM.dynamicFormTester.showpreview',label='Preview')
        bc.dataController("bc.setRegionVisible('bottom',prev)",bc=bc.js_widget,prev='^#FORM.dynamicFormTester.showpreview')
        fb = bar.fbfields.formbuilder(cols=2, border_spacing='2px')
        fb.numberTextBox(value='^#FORM.record.df_fbcolumns',lbl='!!N. Col',width='3em',default_value=1)
        fb.textbox(value='^#FORM.record.df_colswith',lbl='!!Colswith',width='10em')

        return th

    def df_fieldsBagGrid(self,pane,mastertable=None,**kwargs):
        rootcode = '%s_df' %mastertable.replace('.','_')
        bh = pane.contentPane(datapath='#FORM.%s' %rootcode,nodeId=rootcode,overflow='hidden')
        
        view = bh.bagGrid(frameCode='V_%s' %rootcode,storepath='#FORM.record.df_fields',
                    childname='view',struct=self.df_fieldsBagStruct,
                                grid_selfDragRows=True,
                               datapath='.view',_class='frameGrid',gridEditor=False,
                                grid_connect_moveRow='FIRE .changedBagFields;',                               
                               **kwargs)
        view.grid.dataController("this.form.save();",_fired='^.changedBagFields',_delay=1500)
        form = view.grid.linkedForm(frameCode='F_%s' %rootcode,
                                 datapath='.form',loadEvent='onRowDblClick',
                                 dialog_height='450px',dialog_width='620px',
                                 dialog_title='^.form.ftitle',handlerType='dialog',
                                 childname='form',attachTo=bh,store='memory',default_data_type='T',
                                 store_pkeyField='code')
        view.dataController(""" 
            FIRE #FORM.dynamicFormTester._refresh_fields=genro.getCounter();
                                """,_fired='^#FORM.controller.loaded',_delay=1)
        view.dataController("this.form.save();",_delay=500,_fired='^#FORM.dynamicFormTester.counterChanges')
        form.dataController(""" 
            var parentForm = this.form.getParentForm();
            if(parentForm.changed){
                parentForm.save()
            }""",formsubscribe_onDismissed=True,_delay=1)
        self.df_fieldsBagForm(form)
        return bh

    def df_fieldsTableGrid(self,pane,title=None,searchOn=False,**kwargs):
        return pane.dialogTableHandler(relation='@dynamicfields',
                                        formResource='gnrcomponents/dynamicform/dynamicform:Form',
                                        viewResource='gnrcomponents/dynamicform/dynamicform:View',
                                        grid_selfDragRows=True,configurable=False,default_data_type='T',
                                        grid_onDrag="""
                                        if(dragInfo.dragmode=='cell' && dragInfo.colStruct.field=='code'){
                                            dragValues['text/plain'] = '$'+dragValues['text/plain'];
                                        }
                                        """,
                                        grid_selfsubscribe_onExternalChanged="""
                                                        FIRE #FORM.dynamicFormTester._refresh_fields = genro.getCounter();
                                                """,
                                        searchOn=searchOn,title=title,**kwargs)

    def df_previewForm(self,frame,mastertable=None):
        bar = frame.top.slotToolbar('parentStackButtons,*,tplmenu,3')
        menuslot = bar.tplmenu.div()
        menuslot.div('^#FORM.dynamicFormTester.tplToShow',_class='floatingPopup',font_size='.9em',font_weight='bold',color='#555',cursor='pointer',padding='2px',rounded=4)
        menuslot.menu(_class='smallmenu',values='^#FORM.dynamicFormTester.menuvalues',modifiers='*',action='SET #FORM.dynamicFormTester.tplToShow = $1.label')
        menuslot.dataFormula("#FORM.dynamicFormTester.menuvalues", """'auto,'+custom_templates.keys().join(",");""",
                        custom_templates='^#FORM.record.df_custom_templates',_if='custom_templates && custom_templates.len()',
                        _else='"auto"',_delay=1)
        menuslot.dataFormula("#FORM.dynamicFormTester.tplToShow","'auto'",_fired='^#FORM.record.loaded')
        
        bc = frame.center.borderContainer()
        bc.contentPane(region='right',width='40%',splitter=True,padding='15px',background='#eee').div(innerHTML='^#FORM.dynamicFormTester.tplRendered',background='white',shadow='3px 3px 6px gray',padding='4px',rounded=4)
        bc.data('#FORM.dynamicFormTester.data',Bag())
        bc.dataFormula("#FORM.dynamicFormTester.tplRendered", "tplToShow=='auto'?currdata.getFormattedValue():dataTemplate(custom_templates.getItem(tplToShow+'.tpl'),currdata);",
                       custom_templates='^#FORM.record.df_custom_templates',
                       currdata='^#FORM.dynamicFormTester.data',
                       tplToShow='^#FORM.dynamicFormTester.tplToShow',
                        _delay=100,_if='tplToShow')
        bc.dataController("currdata.clear();",_fired='^#FORM.pkey',currdata='=#FORM.dynamicFormTester.data')
        
        bc.contentPane(region='center').dynamicFieldsTestPane(df_table=mastertable,df_pkey='^#FORM.pkey',
                                                    _fired='^#FORM.dynamicFormTester._refresh_fields',
                                                    datapath='#FORM.dynamicFormTester.data',_if='showpreview',showpreview='^#FORM.dynamicFormTester.showpreview')


    @struct_method
    def df_dynamicFieldsTestPane(self,pane,df_table=None,df_pkey=None,**kwargs):
        pane.contentPane().remote(self.df_remoteDynamicForm,df_table=df_table,df_pkey=df_pkey,df_is_new=True,cachedRemote=True,**kwargs)
        
    @struct_method
    def df_dynamicFieldsPane(self,pane,field=None,**kwargs):
        column = self.db.model.column(field) if '.' in field else self.db.table(pane.getInheritedAttributes()['table']).column(field)
        df_field = column.attributes['subfields']
        df_column = column.table.column(df_field)
        df_table = df_column.relatedTable()
        pane.attributes['_workspace'] = True
        pane.attributes.update(overflow='hidden')
        pane.dataController("""
            if(_reason!='container' || this.form.isNewRecord()){
                PUT #FORM.record.%s = null;
            }
            FIRE #FORM.changed_df_type_%s;
        """ %(field,field),df_pkey='^#FORM.record.%s' %df_field,_delay=1)
        pane.contentPane().remote(self.df_remoteDynamicForm,df_table=df_table.fullname,
                            _fired='^#FORM.changed_df_type_%s' %field,
                            df_pkey='=#FORM.record.%s' %df_field,datapath='#FORM.record.%s' %field,
                            df_is_new='== !this.getRelativeData("#FORM.record.%s")' %field,
                            _onRemote="""
                                        //var dataNode = this.form.getFormData().popNode('%s');
                                        //this.setRelativeData('#FORM.record.%s', dataNode._value);
                                        this.form.checkInvalidFields();
                                       """ %(df_field,df_field),
                                       **kwargs)
  


    def df_prepareGlobalVars(self,global_fields=None,df_groups=None):
        result = []
        for n in df_groups:
            ext_ref = n.attr.get('external_ref')
            if ext_ref:
                for f in global_fields[n.attr['pkey']]:
                    result.append('%s.%s' %(ext_ref,f['code'])) 
        return result

    @public_method
    def df_remoteDynamicForm(self,pane,df_table=None,df_pkey=None,datapath=None,df_groups_cols=None,df_groups=None,**kwargs):
        if not (df_pkey or df_groups):
            pane.div()
            return
        pane.attributes.update(kwargs)
        df_tblobj = self.db.table(df_table)
        pkeylist = df_groups.digest('#a.pkey') if df_groups else [df_pkey]
        global_fields = dict([(pkey,df_tblobj.df_getFieldsRows(pkey=pkey)) for pkey in pkeylist])
        if df_groups:
            groupfb = pane.div(padding='10px').formbuilder(cols=df_groups_cols or 1,border_spacing='3px',datapath=datapath,tdl_hidden=True)
            global_vars = self.df_prepareGlobalVars(global_fields=global_fields,df_groups=df_groups)
            for gr in df_groups:
                gr_attr=gr.attr
                pkey=gr_attr['pkey']
                rowspan=gr_attr.get('rowspan',1)
                colspan=gr_attr.get('colspan',1)
                group_code = gr_attr['group_code']
                group_label = gr_attr.get('group_label')
                caption_field = df_tblobj.attributes['caption_field']
                ncol,caption =df_tblobj.readColumns(columns='df_fbcolumns,$%s' %caption_field,pkey=pkey)
                box = groupfb.div(_class='pbl_roundedGroup',datapath='.%s' %(group_code),margin='2px',colspan=colspan,rowspan=rowspan)
                box.div('%s (%s)' %(caption,group_label) if group_label else caption,_class='pbl_roundedGroupLabel')
                grp=box.div(margin_right='10px')
                fields = global_fields[pkey]
                if fields:
                    grp.dynamicFormGroup(fields=fields,ncol=ncol,global_vars=global_vars if gr_attr.get('global_namespace') else None,**kwargs)
        else:
            ncol,colswith = df_tblobj.readColumns(columns='$df_fbcolumns,$df_colswith',pkey=df_pkey)
            fields = global_fields[df_pkey]
            pane.dynamicFormPage(fields=fields,ncol=ncol,colswith=colswith or None,datapath=datapath,**kwargs)

    @struct_method
    def df_dynamicFormPage(self,pane,fields=None,ncol=None,colswith=None,datapath=None,**kwargs):
        fdict = dict()
        for r in fields:
            page = r.pop('page',None) or 'Main'
            fdict.setdefault(page,[]).append(r)
        if len(fdict)==1:
            pane.div(margin_right='10px',datapath=datapath,padding='10px').dynamicFormGroup(fields=fields,ncol=ncol,colswith=colswith or None,**kwargs)
            return
        tc = pane.tabContainer(datapath=datapath,margin='2px')
        pages = fdict.keys()
        if 'Main' in pages:
            pages.remove('Main')
            pages = ['Main']+pages
        for p in pages:
            pane = tc.contentPane(title=p,padding='10px')
            pane.dynamicFormGroup(fdict[p],ncol=ncol,colswith=colswith,**kwargs)

    @struct_method
    def df_dynamicFormGroup(self,pane,fields=None,ncol=None,colswith=None,setInAttributes=False,**kwargs):
        fb = pane.div(margin_right='10px').formbuilder(cols=ncol or 1,keeplabel=True,colswith=colswith,width='100%',tdf_width='100%',lbl_white_space='nowrap')        
        fb.addDynamicFields(fields=fields,setInAttributes=setInAttributes,**kwargs)

    @struct_method
    def df_addDynamicFields(self,fb,fields=None,setInAttributes=None,**kwargs):
        dbstore_kwargs = dictExtract(kwargs,'dbstore_',pop=True)
        if not fields:
            return
        fieldPrefix = '.?' if setInAttributes else '.'
        for r in fields:
            fb.dynamicField(r,fields=fields,dbstore_kwargs=dbstore_kwargs,fieldPrefix=fieldPrefix,**kwargs)
            
    @struct_method
    def df_dynamicField(self,fb,r,fields=None,dbstore_kwargs=None,**kwargs):
        attr = dict(r)
        attr.pop('id',None)
        attr.pop('pkey',None)
        attr.pop('maintable_id',None)
        data_type = attr.pop('data_type','T')
        tag =  attr.pop('wdg_tag') or AUTOWDG[data_type]
        return self.df_makeDynamicField(fb,tag=tag,wdg_attr=attr,data_type=data_type,fields=fields,dbstore_kwargs=dbstore_kwargs,**kwargs)

    @customizable
    def df_makeDynamicField(self,fb,tag=None,wdg_attr=None,data_type=None,fields=None,dbstore_kwargs=None,fieldPrefix=None,df_is_new=None,**kwargs):
        mask = wdg_attr.pop('field_mask',None)
        if tag.endswith('_nopopup'):
            tag = tag.replace('_nopopup','')
            wdg_attr['popup'] = False
        wdg_attr['tag'] =tag
        #wdg_attr['colspan'] = col_max if data_type == 'TL' else 1
        code = wdg_attr.get('code')
        description = wdg_attr.pop('description','')
        fieldPrefix = fieldPrefix or '.'
        wdg_attr['value']='^%s%s' %(fieldPrefix,code)
        if tag.lower() in ('checkbox' or 'radiobutton'):
            wdg_attr['label'] = description
        else:
            wdg_attr['lbl'] = description
        wdg_attr['ghost'] = wdg_attr.pop('field_placeholder',None)
        wdg_attr['tip'] = wdg_attr.pop('field_tip',None)
        wdg_attr['style'] = wdg_attr.pop('field_style',None)
        
        wdg_attr['format'] = wdg_attr.pop('field_format',None)
        wdg_attr['dtype'] = data_type
        wdg_attr['mask'] = mask
        wdg_attr['colspan'] = 1
        wdg_kwargs = wdg_attr.pop('wdg_kwargs',None)
        if wdg_kwargs:
            if isinstance(wdg_kwargs,basestring):
                wdg_kwargs = Bag(wdg_kwargs)
            wdg_kwargs = wdg_kwargs.asDict(ascii=True)
            wdg_attr.update(wdg_kwargs)
            for dim in ('height','width','crop_height','crop_width'):
                c = wdg_attr.pop(dim, None)
                if isinstance(c,int) or (c and c.isdigit()):
                    wdg_attr[dim] = '%spx' %c if c else None
                else:
                    wdg_attr[dim] = c
            wdg_attr['colspan'] = wdg_attr.pop('colspan',1) or 1
        if tag.lower()=='simpletextarea':
            wdg_attr.setdefault('speech',True)
            wdg_attr['width'] = wdg_attr.get('width') or '94%'
        customizer = getattr(self,'df_%(tag)s' %wdg_attr,None)
        if customizer:
            customizer(wdg_attr,dbstore_kwargs=dbstore_kwargs)
        dictExtract(wdg_attr,'source_',pop=True)
        self._df_handleFieldFormula(wdg_attr,fb=fb,fields=fields,**kwargs)
        self._df_handleFieldValidation(wdg_attr,fields=fields)
        code = wdg_attr.pop('code')
        getter = wdg_attr.pop('getter',None)
        default_value = wdg_attr.pop('default_value',None)
        if default_value is not None and df_is_new:
            print 'SET setting default for ',code
            fb.data('.%s' %code,default_value)
        wdg = self.df_child(fb,**wdg_attr)
        if not getter:
            return wdg     
        if isinstance(getter,basestring):
            getter = Bag(getter)
        if getter['table']:
            self._df_handleGetter(fb,code=code,getter=getter)

    @customizable
    def df_child(self,fb,**attr):
        return fb.child(**attr)

    def df_filteringselect(self,attr,**kwargs):
        attr['values'] = attr.get('source_filteringselect')
        
    def df_combobox(self,attr,**kwargs):
        attr['values'] = attr.get('source_combobox')
                
    def df_img(self,attr,**kwargs):
        attr['placeholder'] = self.getResourceUri('images/imgplaceholder.png')
        attr['upload_folder'] = "=='site:'+this.getInheritedAttributes()['table'].replace('.','/')+'%(code)s'" %attr
        attr['upload_filename'] = '=#FORM.pkey'
        attr['edit'] = True
        attr['src'] = attr.pop('value',None)
        attr['border'] = '1px solid silver'
        attr['shadow'] = '2px 2px 3px #555'

    def df_graph(self,attr,**kwargs):
        attr['tag'] = 'div'
        attr['innerHTML'] = 'Not yet implemented'
        pass

    def df_dbselect(self,attr,dbstore_kwargs=None,**kwargs):
        tbl = attr.get('source_dbselect')
        attr['dbtable'] = tbl
        pkg,tblname = tbl.split('.')
        attr['hasDownArrow'] =True
        if pkg in dbstore_kwargs:
            attr['_storename'] = '=%s' %dbstore_kwargs[pkg]

    def df_checkboxtext(self,attr,**kwargs):
        attr.setdefault('popup',True)
        attr.setdefault('codeSeparator',False)
        attr['values'] = attr.get('source_checkboxtext')    
    
    def df_horizontalslider(self,attr,dbstore_kwargs=None,**kwargs):
        if attr['tag'].lower()=='horizontalslider' and attr.get('validate_range'):
            attr['min'], attr['max'] = attr['validate_range'].split(':')
            attr.pop('validate_range')
            attr['intermediateChanges'] = True
            if not attr.get('width'):
                attr['width'] = '200px'
    
    def _df_handleFieldFormula(self,attr,fb,fields=None,global_vars=None,**kwargs):
        formula = attr.pop('formula',None)
        if not formula:
            return
        formulaArgs = dict([(str(x['code']),'^.%s' %x['code']) for x in fields if x['code'] in formula])
        if global_vars:
            formulaArgs.update(dict([(str(x.replace('.','_')),'^.#parent.%s' %x) for x in global_vars if x.replace('.','_') in formula]))
        formulaArgs['_'] = """==this._relativeGetter('#FORM.record');"""
        fb.dataFormula(".%s" %attr['code'], "dynamicFormHandler.executeFormula(this,_expression,'_expression');",result_type=attr.get('dtype') ,_expression=formula,_init=True,**formulaArgs)
        attr['readOnly'] =True 
    

    def _df_handleGetter(self,fb,code=None,getter=None):
        kw = asDict(getter['where'].replace('\n',','))
        _iflist = [k for k,v in kw.items() if v.startswith('^') or v.startswith('=')]
        if _iflist:
            kw['_if'] = ' && '.join(_iflist)
        fb.dataRemote('.%s' %code,self._df_remoteGetter,table=getter['table'],column=getter['column'],innerpath=getter['innerpath'],**kw)

    @public_method
    def _df_remoteGetter(self,table=None,column=None,innerpath=None,**kwargs):
        rec = self.db.table(table).record(ignoreDuplicate=True,ignoreMissing=True,**kwargs).output('dict')
        if rec:
            return rec[column][innerpath] if innerpath else rec[column]

    def _df_handleFieldValidation(self,attr,fields):
        if attr.get('validate_range'):
            r = attr.pop('validate_range')
            min_v,max_v = r.split(':')
            if min_v or max_v:
                attr['validate_min'] = min_v or None
                attr['validate_max'] = max_v or None
                attr['validate_min_error'] = '!!Under min value %s' %min_v
                attr['validate_max_error'] = '!!Over max value %s' %max_v
        if attr.get('validate_case'):
            attr['validate_case'] = attr.pop('validate_case')
        if attr.get('mandatory'):
            attr['validate_notnull'] = attr.pop('mandatory')            
        if attr.get('field_visible'):
            condition = attr.pop('field_visible')
            tpv = ("", "",attr['code'])
            if attr.get('validate_notnull'):
                attr['validate_notnull']  = "^#WORKSPACE.%s.do_validations" %attr['code']
                tpv = ("sourceNode.setRelativeData('#WORKSPACE.%s.do_validations',true);" %attr['code'], "sourceNode.setRelativeData('#WORKSPACE.%s.do_validations',false);" %attr['code'],attr['code'])
            attr['row__formulaVisibleIf'] = condition
            attr['row_hidden'] = """==function(sourceNode){
                                        var __c = dynamicFormHandler.executeFormula(sourceNode,sourceNode.attr._formulaVisibleIf,'hidden');
                                        try{
                                            if(__c){
                                                %s
                                                return false;
                                            }else{
                                                %s
                                                sourceNode.setRelativeData('.%s',null);
                                                return true;
                                            }
                                        }catch(e){
                                            alert(e.toString());
                                        }
                                    }(this);""" %tpv

            conditionArgs = dict([('row_%s' %str(x['code']),'^.%s' %x['code']) for x in fields if x['code'] in condition])
            attr.update(conditionArgs)

            
    