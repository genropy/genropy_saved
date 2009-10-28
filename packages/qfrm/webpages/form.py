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
        fb = top.formbuilder(cols=2, margin_left='2em',border_spacing='5px',margin_top='1em',disabled=disabled, width='600px')
        width='100%'
        fb.field('code',width='10em', colspan=1)
        fb.field('name',width=width, colspan=1)
        self.sectionsContainer(bc.borderContainer(region='center', _class='pbl_roundedGroup',margin='0px'),disabled=True)
        
    def formOtherParsTab(self,pane,disabled=True):
        #pane.div('!!Other Parameters',_class='pbl_roundedGroupLabel')
        fb = pane.formbuilder(cols=3, margin_left='2em',border_spacing='5px',margin_top='1em',disabled=disabled, width='600px')
        width='100%'
        fb.field('long_name',width=width,colspan=2)
        fb.field('pkg_table',width='10em', colspan=1)
        fb.field('bag_field',width=width, colspan=1)
        fb.field('sort_order',width=width,colspan=1)
        fb.field('version',width='10em', colspan=1)
        fb.simpleTextarea(lbl='CSS',value='^.css',lbl_vertical_align='top', width=width, height='10em', colspan=3)

    def previewTab(self, pane, **kwargs):
            pass

    def orderBase(self):
        return 'name'
    
    def queryBase(self):
        return dict(column='name',op='contains', val='%', runOnStart=True)

#-------------- BEGIN SECTION --------------------
        
    def sectionsContainer(self, bc, **kwargs):
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
                               name:10,
                               long_name:20,
                               sort_order:10
                               """,
                    selectionPars = dict(where='$form_id =:form_id',
                                         form_id='=form.record.id',
                                         _if='form_id', order_by='$sort_order',
                                         _else='null'))

        self.recordDialog('qfrm.section',firedPkey='^#sectionGrid.firedPkey',
                        default_form_id='=form.record.id',
                        onSaved='FIRE #sectionGrid.reload;', 
                        height='500px',width='500px',title='!!Section',
                        formCb=self.sectionIncludedForm,savePath='aux_sections.lastSaved') # the default is the id of the last record you have touched + attributes (the resultAttr)
                        
        
    def sectionController(self, bc, **kwargs):

        #adding section
        bc.dataController("""FIRE .firedPkey;""",
                        _fired="^.addingRecord",
                        section_id='=form.record.id', _if='section_id',
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
        pane = recordBC.contentPane(_class='pbl_roundedGroup',**kwargs)
        self.sectionForm(pane)

    def sectionForm(self, pane):
        fb = pane.formbuilder(cols=1, margin_left='1em',border_spacing='5px',dbtable='qfrm.section')
        fb.field('code', width='10em')
        fb.field('name', width='10em')
        fb.field('long_name', width='10em')
        fb.field('sort_order',width='10em')


#-------------- END section --------------------

