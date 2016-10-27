#!/usr/bin/python
# -*- coding: UTF-8 -*-

from gnr.web.gnrbaseclasses import BaseComponent
from gnr.core.gnrdecorator import public_method

class View(BaseComponent):

    def th_struct(self,struct):
        r = struct.view().rows()
        r.fieldcell('tbl_key')
        r.fieldcell('tbl')
        r.fieldcell('pkg')
        r.fieldcell('description')

    def th_order(self):
        return 'tbl_key'

    def th_query(self):
        return dict(column='tbl_key', op='contains', val='')


    def th_top_custom(self,top):
        top.bar.replaceSlots('searchOn','searchOn,sections@pkg')

    def th_options(self):
        return dict(virtualStore=False)

class ViewFromPackage(BaseComponent):

    def th_struct(self,struct):
        r = struct.view().rows()
        r.fieldcell('tbl_key')
        r.fieldcell('tbl')
        r.fieldcell('description')

    def th_order(self):
        return 'tbl_key'

    def th_query(self):
        return dict(column='tbl_key', op='contains', val='')

    def th_options(self):
        return dict(virtualStore=False)


class Form(BaseComponent):

    def th_form(self, form):
        bc = form.center.borderContainer()
        fb = bc.contentPane(region='top',datapath='.record',nodeId='tblinfo_rec').formbuilder(cols=3, border_spacing='4px')
        fb.field('pkg')
        fb.field('tbl')
        fb.field('branch')
        fb.field('description',colspan=3,width='100%')
        tc = bc.tabContainer(region='center',margin='2px')
        self.qtreeItems(tc.contentPane(title='Quick Fields Tree'))
        self.authorizationsItems(tc.contentPane(title='Authorization'))

    def authorizationsItems(self,pane):
        pane.dialogTableHandler(relation='@items',condition='$item_type=:t',nodeId='auth_#',
                                condition_t='AUTH',default_item_type='AUTH',
                                viewResource='AuthItemView',formResource='AuthItemForm')


    def qtreeItems(self,pane):
        frame = pane.multiButtonForm(frameCode='qtree_#',relation='@items',
                                condition='$item_type=:t',
                                condition_t='QTREE',default_item_type='QTREE',
                                caption='description',
                                datapath='#FORM.thqt',
                                #viewResource='QTREEItemView',
                                formResource='QTREEItemForm',
                                multibutton_deleteSelectedOnly=True,
                                margin='3px',border='1px solid silver')
        frame.multiButtonView.item(code='add_it',caption='+',frm=frame.form.js_form,
                                    action='frm.newrecord({code:custom_code || standard_code,description:custom_description || description || custom_code});',
                                    ask=dict(title='New Item',fields=[dict(lbl='Standard code',
                                                                    name='standard_code',tag='remoteSelect',
                                                                    auxColumns='code,description',
                                                                    method='_table.adm.tblinfo_item.getFilteredOptions',
                                                                    condition_tbl='=#tblinfo_rec.tbl_key',
                                                                    condition_item_type='QTREE',
                                                                    selected_description='.description',
                                                                    values=self.db.table('adm.user_tblinfo').type_QTREE(),
                                                                    hasDownArrow=True),
                                                                dict(lbl='Custom code',
                                                                    name='custom_code',disabled='^.standard_code'), 
                                                                dict(lbl='Custom description',
                                                                    name='custom_description',disabled='^.standard_code')],
                                                               ),
                parentForm=True,deleteAction=False)


    def th_options(self):
        return dict(dialog_parentRatio=0.9)

class FormFromTH(Form):
    def th_form(self, form):
        tc = form.center.tabContainer(margin='3px')
        self.qtreeItems(tc.contentPane(title='Quick Fields Tree'))
        self.authorizationsItems(tc.contentPane(title='Authorization'))

    def th_options(self):
        return dict(dialog_parentRatio=0.9,showtoolbar=False)

class FormFromPackage(Form):

    def th_form(self, form):
        bc = form.center.borderContainer()
        fb = bc.contentPane(region='top',datapath='.record').formbuilder(cols=2, border_spacing='4px')
        fb.field('tbl')
        fb.field('description')
        tc = bc.tabContainer(region='center',margin='2px')
        self.authorizationsItems(tc.contentPane(title='Authorization'))

