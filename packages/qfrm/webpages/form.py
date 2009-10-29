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
                  name:10,
                  long_name:10,
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
        fb.field('name',width='30em', colspan=1)
        self.sectionContainer(bc.borderContainer(region='center', _class='pbl_roundedGroup',margin='0px'),disabled=True)
        
    def formOtherParsTab(self,pane,disabled=True):
        #pane.div('!!Other Parameters',_class='pbl_roundedGroupLabel')
        fb = pane.formbuilder(cols=3, margin_left='2em',border_spacing='5px',margin_top='1em',disabled=disabled, width='600px')
        width='100%'
        fb.field('code',width='10em', colspan=1)
        fb.field('name',width=width, colspan=2)
        fb.field('pkg_table',width='10em', colspan=1)
        fb.field('long_name',width=width,colspan=2)
        fb.field('bag_field',width=width, colspan=1)
        fb.field('sort_order',width=width,colspan=1)
        fb.field('version',width='10.1em', colspan=1)
        fb.simpleTextarea(lbl='CSS',value='^.css',lbl_vertical_align='top', width=width, height='10em', colspan=3)
        helptext="""<ul><li>Code - the identifier of this form</li>
                    <li>Name - The short name used in the tab of main page for the form</li>
                    <li>Package.Table - This must be a valid package and table name separated by a period. It is used to identify which
                        table the xml column is placed to hold the custom data entered into the form</li>
                    <li>Long Name - is the more description name for this form useful for reports</li>
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
        return 'name'
    
    def queryBase(self):
        return dict(column='name',op='contains', val='%', runOnStart=True)

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
                               name/Name (Tab):10,
                               long_name:20,
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
        self.formItemContainer(bottom)

    def formItemContainer(self, bc):
        pass

    def sectionForm(self, pane):
        fb = pane.formbuilder(cols=3, margin_left='1em',border_spacing='5px',dbtable='qfrm.section', width='550px')
        fb.field('code', width='7em', colspan=1)
        fb.field('name', width='100%', colspan=2)
        fb.field('long_name', width='100%', colspan=3)
        fb.field('sort_order',width='7em', colspan=1)
        fb.field('cols',width='4em', colspan=1)
        fb.field('rows',width='100%', colspan=1) #, lbl_width='5em'
        

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
                        onSaved='FIRE #groupGrid.reload;', 
                        height='150px',width='300px',title='!!Group',
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
        fb = pane.formbuilder(cols=2, margin_left='1em',border_spacing='5px',dbtable='qfrm.group', width='270px')
        fb.field('code', width='5em', colspan=2)
        fb.field('label', width='100%', colspan=2)
        fb.field('x_position', width='3.5em')
        fb.field('y_position',width='100%')
        fb.field('colspan',width='3.5em')
        fb.field('rowspan',width='100%')
        pane.div('<HR>', margin_left='10px', margin_right='10px')

#-------------- END GROUP --------------------
