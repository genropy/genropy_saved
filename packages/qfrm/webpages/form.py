#!/usr/bin/env python
# encoding: utf-8
"""
form.py

Created by Jeff Edwards on 2009-01-21.
Copyright (c) 2008 Goodsoftware Pty Ltd All rights reserved.
"""
import os
#from gnr.web.gnrwebpage import GnrWebPage
from gnr.core.gnrbag import Bag

# --------------------------- GnrWebPage subclass ---------------------------
class GnrCustomWebPage(object):
    maintable='qfrm.form'
    py_requires='public:Public,standard_tables:TableHandler'
    py_requires="""public:Public,standard_tables:TableHandler,
                   public:IncludedView,public:RecordHandler
                   """

    def windowTitle(self):
        return '!!Form'

    def pageAuthTags(self, method=None, **kwargs):
        return 'user'
        
    def tableWriteTags(self):
        return 'user'
        
    def tableDeleteTags(self):
        return 'user'
        
    def barTitle(self):
        return '!!Definition'
        
    def columnsBase(self,):
        return """
                  code:10,
                  label:10,
                  name:10,
                  pkg_table:10,
                  bag_field:10,
                  version:5,
                  css
               """
    # look to this url for info on formatting   http://www.unicode.org/reports/tr35/tr35-4.html#Date_Format_Patterns

    def formBase(self, parentBC,  disabled=False, **kwargs):
        bc=parentBC.borderContainer(**kwargs)
        center = bc.tabContainer(region='center', selected='^aux_tab.selectedPage')
        self.formMainTab(center.borderContainer(title='Form',design='sidebar'),disabled=disabled)
        self.formOtherParsTab(center.borderContainer(title='Other Parameters',design='sidebar'),disabled=disabled)
        self.previewTab(center.borderContainer(title='Preview',design='sidebar'),disabled=disabled)
        
    def formMainTab(self,bc,disabled=True, **kwargs):
        self.deletingRecordMsg ="""!!You are deleting a %s from the database. 
                        You cannot undo this operation, are you sure you wish to proceed?"""
        self.addingRecordMsg = "!!You must save the form record before adding any %s"
        top = bc.contentPane(region='top', height='60px', _class='pbl_roundedGroup',margin='0px')
        #top.div('!!Form',_class='pbl_roundedGroupLabel')
        fb = top.formbuilder(cols=2, margin_left='2em',border_spacing='5px',margin_top='1em',disabled=disabled)
        fb.field('code',width='10em', colspan=1)
        fb.field('label', lbl='Form Label', lbl_width='8em', width='30em', colspan=1)
        self.sectionContainer(bc.borderContainer(region='center', _class='pbl_roundedGroup',margin='0px'),disabled=True)
        
    def formOtherParsTab(self,pane,disabled=True):
        #pane.div('!!Other Parameters',_class='pbl_roundedGroupLabel')
        fb = pane.formbuilder(cols=3, margin_left='2em',border_spacing='5px',margin_top='1em',disabled=disabled, width='600px')
        width='100%'
        fb.field('code',width='10em', colspan=1)
        fb.field('label',width=width, colspan=2)
        fb.field('pkg_table',width='10em', colspan=1)
        fb.field('name',width=width,colspan=2)
        fb.field('bag_field',width='10em', colspan=1)
        fb.field('sort_order',width='5em',colspan=1)
        fb.field('version', lbl_width='5em', width='100%', colspan=1)
        fb.simpleTextarea(lbl='CSS',value='^.css',lbl_vertical_align='top', width=width, height='10em', colspan=3)
        helptext="""<ul><li>Code - the identifier of this form</li>
                    <li>Label - The label used in the tab of main page for the form</li>
                    <li>Package.Table - This must be a valid package and table name separated by a period. It is used to identify which
                        table the xml column is placed to hold the custom data entered into the form</li>
                    <li>Name - is the more descriptive name for this form useful for reports</li>
                    <li>Bag Field - This is the name of the column in the hosting table for the quick form. It is used to store the data
                        entered into the custom form fields</li>
                    <li>Sort Order - is an alpha numeric field that the tab order is ordered by</li>
                    <li>Version - The version of the form can be used to isolate the form for particular main package codes</li>
                    <li>css - Here the operator can create custom css classes to be used in the section and form items</li></ul>
                    """
        pane.div(helptext, margin='10px', padding='10px', color='#003366')

    def previewTab(self, pane, **kwargs):
            pass

    def orderBase(self):
        return 'label'
    
    def queryBase(self):
        return dict(column='label',op='contains', val='%', runOnStart=True)

#-------------- BEGIN SECTION --------------------
        
    def sectionContainer(self, bc, **kwargs):
        self.includedViewBox(bc,label=u'!!Sections',datapath='aux_sections',
                    table='qfrm.section',
                    add_action='FIRE .addingRecord;',
                    del_action='FIRE .deletingRecord;',
                    addOnCb=self.sectionController,
                    multiSelect=False,
                    nodeId='sectionGrid',
                    reloader='^form.record.id',
                    connect_onRowDblClick="""
                            FIRE .firedPkey = this.widget.rowIdByIndex($1.rowIndex);
                            """,
                    columns="""code:7,
                               label/Tab Label:10,
                               name:20,
                               cols:9,
                               rows:9,
                               sort_order:10
                               """,
                    selectionPars = dict(where='$form_id =:form_id',
                                         form_id='=form.record.id',
                                         _if='form_id', order_by='$sort_order',
                                         _else='null'))

        self.recordDialog('qfrm.section',firedPkey='^#sectionGrid.firedPkey',
                        default_form_id='=form.record.id',
                        onSaved='FIRE #sectionGrid.reload;', 
                        height='600px',width='600px',title='!!Section',
                        formCb=self.sectionIncludedForm,savePath='aux_sections.lastSaved') # the default is the id of the last record you have touched + attributes (the resultAttr)
                        
        
    def sectionController(self, bc, **kwargs):

        #adding section
        bc.dataController("""FIRE .firedPkey;""",
                        _fired="^.addingRecord",
                        form_id='=form.record.id', _if='form_id',
                        _else="genro.dlg.alert(msg)",
                        msg= self.addingRecordMsg % 'Section')

        #deleting section
        bc.dataRpc("dummy",'deleteIncludedViewRecord',table='qfrm.section',
                    rowToDelete="=.selectedId", _fired='^.proceedDelete',
                     _if='rowToDelete', _onResult="""FIRE .reload;""")
                                                       
        bc.dataController("""genro.dlg.ask('Warning',msg,null,resultPathOrActions)""",
                            _fired="^.deletingRecord",
                            msg= self.deletingRecordMsg % 'Section',
                            resultPathOrActions='.proceedDelete')


    def sectionIncludedForm(self,recordBC,**kwargs):
        bc = recordBC.borderContainer(_class='pbl_roundedGroup',**kwargs)
        top=bc.contentPane(region='top', height='80px', _class='pbl_roundedGroup',**kwargs)
        temp=bc.borderContainer(region='center') #, _class='pbl_roundedGroup',**kwargs
        middle=temp.borderContainer(region='top', height='150px', _class='pbl_roundedGroup',**kwargs)
        bottom=temp.borderContainer(region='center', _class='pbl_roundedGroup',**kwargs)
        self.sectionForm(top)
        self.groupContainer(middle)
        self.itemContainer(bottom)


    def sectionForm(self, pane):
        fb = pane.formbuilder(cols=3, margin_left='1em',border_spacing='5px',dbtable='qfrm.section', width='550px')
        fb.field('code', width='7em', colspan=1)
        fb.field('label', width='100%', colspan=2)
        fb.field('name', width='100%', colspan=3)
        fb.field('sort_order',width='7em', colspan=1)
        fb.field('cols',lbl='Columns', width='4em', colspan=1)
        fb.field('rows',lbl='Rows', lbl_width='5em', width='4em', colspan=1) #, lbl_width='5em'
        

#-------------- END section --------------------

#-------------- BEGIN GROUP --------------------
        
    def groupContainer(self, bc, **kwargs):
        self.includedViewBox(bc,label=u'!!Groups',datapath='aux_groups',
                    table='qfrm.group',
                    add_action='FIRE .addingRecord;',
                    del_action='FIRE .deletingRecord;',
                    addOnCb=self.groupController,
                    multiSelect=False,
                    nodeId='groupGrid',
                    reloader='^aux_sections.selectedId',
                    connect_onRowDblClick="""
                            FIRE .firedPkey = this.widget.rowIdByIndex($1.rowIndex);
                            """,
                    columns="""code:7,
                               label:13,
                               x_position:8,
                               y_position:8,
                               colspan:7,
                               rowspan:7
                               """,
                    selectionPars = dict(where='$section_id =:section_id',
                                         section_id='=aux_sections.selectedId',
                                         _if='section_id', order_by='$label',
                                         _else='null'))

        self.recordDialog('qfrm.group',firedPkey='^#groupGrid.firedPkey',
                        default_section_id='=aux_sections.selectedId',
                        default_lblpos='L',
                        default_lblalign='left', default_fldalign='left',default_lblvalign='middle', default_fldvalign='middle',
                        default_x_position=1, default_y_position=1,default_rows=1, default_cols=1,default_colspan=1, default_rowspan=1,
                        default_lblclass='gnrfieldlabel',
                        onSaved='FIRE #groupGrid.reload;', 
                        height='300px',width='400px',title='!!Group',
                        formCb=self.groupIncludedForm,savePath='aux_groups.lastSaved') # the default is the id of the last record you have touched + attributes (the resultAttr)
                        
        
    def groupController(self, bc, **kwargs):

        #adding section
        bc.dataController("""FIRE .firedPkey;""",
                        _fired="^.addingRecord",
                        section_id='=aux_sections.selectedId', _if='section_id',
                        _else="genro.dlg.alert(msg)",
                        msg= self.addingRecordMsg % 'Group')

        #deleting section
        bc.dataRpc("dummy2",'deleteIncludedViewRecord',table='qfrm.group',
                    rowToDelete="=.selectedId", _fired='^.proceedDelete',
                     _if='rowToDelete', _onResult="""FIRE .reload;""")
                                                       
        bc.dataController("""genro.dlg.ask('Warning',msg,null,resultPathOrActions)""",
                            _fired="^.deletingRecord",
                            msg= self.deletingRecordMsg % 'Group',
                            resultPathOrActions='.proceedDelete')


    def groupIncludedForm(self,recordBC,**kwargs):
        pane = recordBC.contentPane(_class='pbl_roundedGroup',**kwargs)
        self.groupForm(pane)
        

    def groupForm(self, pane):
        leftwidth='6em'
        rightwidth='100%'
        fb = pane.formbuilder(cols=2, margin_left='1em',border_spacing='5px',dbtable='qfrm.group', width='350px')
        fb.field('code', width=leftwidth, colspan=2)
        fb.field('label', width=rightwidth, colspan=2)
        fb.field('lblclass',width=rightwidth, colspan=2)
        fb.div('', colspan=2)
        fb.field('x_position', width=leftwidth, tag='numberSpinner')
        fb.field('colspan',width=rightwidth, tag='numberSpinner')
        fb.field('y_position',width=leftwidth, tag='numberSpinner')
        fb.field('rowspan',width=rightwidth,tag='numberSpinner')
        fb.field('lblpos',width=leftwidth, colspan=1, tag='filteringSelect', values='L:Left,T:Top') # L, T
        fb.field('cols',width=rightwidth, tag='numberSpinner', tooltip='Number of columns for the inner form') # columns in the inner form builder
        fb.div('')
        fb.field('rows',width=rightwidth, tag='numberSpinner', tooltip='Number of rows for the inner form') # optional rows in the inner form builder
        fb.field('lblalign',width=leftwidth, tag='filteringSelect', values='left:left,right:right,center:center,justify:justify,char:char')
        fb.field('lblvalign',width=rightwidth, tag='filteringSelect', values='top:top,middle:middle,bottom:bottom,baseline:baseline')
        fb.field('fldalign',width=leftwidth, tag='filteringSelect', values='left:left,right:right,center:center,justify:justify,char:char') 
        fb.field('fldvalign',width=rightwidth, tag='filteringSelect', values='top:top,middle:middle,bottom:bottom,baseline:baseline')
        pane.div('<BR><BR><HR>', margin_left='10px', margin_right='10px')
        
# def formbuilder(self, cols=1, dbtable=None, tblclass='formbuilder',
#                      lblclass='gnrfieldlabel', lblpos='L', _class='', fieldclass='gnrfield',
#                      lblalign=None, lblvalign='middle',
#                      fldalign=None, fldvalign='middle', disabled=False,
#                      rowdatapath=None, head_rows=None, **kwargs):
        
# http://www.w3schools.com/Css/pr_pos_vertical-align.asp
# this vertical-align property is misnamed and is not inherited and has values of:
# length    Raises or lower an element by the specified length. Negative values are allowed
# % Raises or lower an element in a percent of the "line-height" property. Negative values are allowed
# baseline  Align the baseline of the element with the baseline of the parent element. This is default
# sub   Aligns the element as it was subscript
# super Aligns the element as it was superscript
# top   The top of the element is aligned with the top of the tallest element on the line
# text-top  The top of the element is aligned with the top of the parent element's font
# middle    The element is placed in the middle of the parent element
# bottom    The bottom of the element is aligned with the lowest element on the line
# text-bottom   The bottom of the element is aligned with the bottom of the parent element's font
# inherit   Specifies that the value of the vertical-align property should be inherited from the parent element


#-------------- END GROUP --------------------

#-------------- BEGIN ITEM --------------------
        
    def itemContainer(self, bc, **kwargs):
        self.includedViewBox(bc,label=u'!!Items',datapath='aux_items',
                    table='qfrm.item',
                    add_action='FIRE .addingRecord;',
                    del_action='FIRE .deletingRecord;',
                    addOnCb=self.itemController,
                    multiSelect=False,
                    nodeId='itemGrid',
                    reloader='^aux_sections.selectedId',
                    connect_onRowDblClick="""
                            FIRE .firedPkey = this.widget.rowIdByIndex($1.rowIndex);
                            """,
                    columns="""short_code:7,
                               @group_id.label/Group:13,
                               label/Item Label:13,
                               colspan:7,
                               rowspan:7
                               """,
                    selectionPars = dict(where='$section_id =:section_id',
                                         section_id='=aux_sections.selectedId',
                                         _if='section_id', order_by='$label',
                                         _else='null'))

        self.recordDialog('qfrm.item',firedPkey='^#itemGrid.firedPkey',
                        default_section_id='=aux_sections.selectedId',
                        onSaved='FIRE #itemGrid.reload;', 
                        height='600px',width='800px',title='!!Item',
                        formCb=self.itemIncludedForm,savePath='aux_items.lastSaved') # the default is the id of the last record you have touched + attributes (the resultAttr)
                        
        
    def itemController(self, bc, **kwargs):

        #adding item
        bc.dataController("""FIRE .firedPkey;""",
                        _fired="^.addingRecord",
                        section_id='=aux_sections.selectedId', _if='section_id',
                        _else="genro.dlg.alert(msg)",
                        msg= self.addingRecordMsg % 'Item')

        #deleting item
        bc.dataRpc("dummy3",'deleteIncludedViewRecord',table='qfrm.item',
                    rowToDelete="=.selectedId", _fired='^.proceedDelete',
                     _if='rowToDelete', _onResult="""FIRE .reload;""")
                                                       
        bc.dataController("""genro.dlg.ask('Warning',msg,null,resultPathOrActions)""",
                            _fired="^.deletingRecord",
                            msg= self.deletingRecordMsg % 'Item',
                            resultPathOrActions='.proceedDelete')


    def itemIncludedForm(self,recordBC,**kwargs):
        #print 'kwargs: ', kwargs  disabled and the table qfrm.item
        bc = recordBC.borderContainer(_class='pbl_roundedGroup',**kwargs)
        self.leftItemFormPane(bc.contentPane(region='left',width='400px', _class='pbl_roundedGroup',**kwargs), disabled=True)
        self.rightItemFormPane(bc.contentPane(region='center', _class='pbl_roundedGroup',**kwargs))

        
    def rightItemFormPane(self, pane, disabled=False, **kwargs):
        pane.dataFormula('aux.fb_class','"answer_type_"+ansType',ansType='^.answer_type')
        pane=pane.div(_class='^aux.fb_class')

        fb = pane.formbuilder(cols=1, dbtable='qfrm.item', margin_left='1em', border_spacing='5px', margin_top='1em',width='90%',disabled=disabled)
        lblwidth='90px'
        fb.div(lbl="""Setting the answer type will determine the widget used on the form.  You can also set the colspan, sort order,
                      and the value list.  The value list is comma delimited used for a popup.""",lbl_colspan=2,  lbl_class='helptext', lbl_padding_top='0px', lbl_padding_bottom='10px', lbl_width=lblwidth)

        fb.field('answer_type',width='10em', tag='filteringSelect',nodeId='testfilter',
                               values='B:CheckBox,D:Date Field,R:Float Field,L:Integer Field,A:Text Field,T:Text Area Field,Z:Form Text',
                               colspan=1, lbl_width=lblwidth)
        fb.field('width', width='5em',colspan=1, lbl_width=lblwidth, row_class='width_field')
        fb.field('height',width='5em',colspan=1, lbl_width=lblwidth, row_class='height_field')
        fb.field('colspan',width='5em',colspan=1, lbl_width=lblwidth)
        fb.field('tooltip',width='20em',colspan=1, lbl_width=lblwidth)
    
        fb.simpleTextarea(lbl='Value List',value='^.value_list', lbl_width=lblwidth, lbl_vertical_align='top', 
                                                                  width='20em',height='5em', colspan=1, row_class='value_list_field')
        fb.field('form_text_style',width='20em',colspan=1, lbl_width=lblwidth, tag='filteringSelect', values='customFormHeader:Heading,customFormBody:Body,customFormFooter:Footer', row_class='form_text_style_field')
        fb.simpleTextarea(lbl='Form Text',value='^.form_text', lbl_width=lblwidth, lbl_vertical_align='top', 
                                                                  width='20em',height='5em', colspan=1, row_class='form_text_field')                                                                  
        fb.simpleTextarea(lbl='Formula',value='^.formula', lbl_width=lblwidth, lbl_vertical_align='top', 
                                                                  width='20em',height='5em', colspan=1, row_class='formula_field')


    def leftItemFormPane(self, pane, disabled=False):
        fb = pane.formbuilder(cols=2, dbtable='qfrm.item', margin_left='1em', border_spacing='5px', margin_top='1em',width='380px',disabled=disabled)
        fld_width='100%'
        lblwidth='100px'
        fb.div(lbl="""Set the details of the question, including its code for query purposes,
                      the label, group and default value""",lbl_colspan=4, colspan=2,  lbl_class='helptext', lbl_padding_bottom='10px', lbl_width=lblwidth)
        
        fb.field('short_code',width='10em',colspan=2, lbl_width=lblwidth)
        fb.field('group_id', lbl='Group',width=fld_width, colspan=2, lbl_width=lblwidth,
                        condition='$section_id =:sectionId' ,condition_sectionId='^aux_sections.selectedId') #exclude=self.getGroupsToExclude(),
        fb.field('code', lbl='Calculated Code', tag='div', colspan=2, lbl_padding_top='5px', padding_top='5px', lbl_width=lblwidth)
        fb.field('label',width=fld_width ,colspan=2, lbl_width=lblwidth)
        fb.field('default_value',width=fld_width,colspan=2, lbl_width=lblwidth)
        fb.field('sort_order',width='7em',colspan=2, lbl_width=lblwidth)

        fb.simpleTextarea(lbl='Question',value='^.name',lbl_vertical_align='top', width=fld_width, height='5em', colspan=2, lbl_width=lblwidth)

        fb.div(lbl="""Set the following fields to make the question specific to a version,to override, or to exclude.""",
                      lbl_colspan=4, colspan=2,  lbl_class='helptext', lbl_padding_top='20px', lbl_padding_bottom='10px', lbl_width=lblwidth)
        fb.field('version', lbl='Version',width=fld_width, colspan=2, lbl_width=lblwidth)
        fb.field('exclude',colspan=2)

       #fb = pane.formbuilder(cols=2, margin_left='1em',border_spacing='5px',dbtable='qfrm.item', width='350px')
       #fb.field('short_code', width='5em', colspan=1)
       #fb.field('group_id', width='15em', colspan=2)
       #fb.field('code', lbl='Calculated Code', tag='div', width='5em', colspan=1)
       #fb.field('label', width='100%', colspan=2)
       #fb.field('colspan', width='3.5em')
       #fb.field('rowspan', width='3.5em')
       #pane.div('<HR>', margin_left='10px', margin_right='10px')

#-------------- END ITEM --------------------
