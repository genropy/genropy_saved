#!/usr/bin/python
# -*- coding: UTF-8 -*-

from gnr.web.gnrbaseclasses import BaseComponent
from gnr.core.gnrdecorator import public_method
from gnr.core.gnrbag import Bag

class View(BaseComponent):

    def th_struct(self,struct):
        r = struct.view().rows()
        r.fieldcell('tblid')
        r.fieldcell('pkgid')
        r.fieldcell('description')

    def th_order(self):
        return 'tblid'

    def th_query(self):
        return dict(column='tblid', op='contains', val='')


    def th_top_custom(self,top):
        top.bar.replaceSlots('searchOn','searchOn,sections@pkgid')

    def th_options(self):
        return dict(virtualStore=False,readOnly=True)

class ViewFromPackage(BaseComponent):

    def th_struct(self,struct):
        r = struct.view().rows()
        r.fieldcell('tblid')
        r.fieldcell('description')

    def th_order(self):
        return 'tblid'


    def th_options(self):
        return dict(virtualStore=False)


class Form(BaseComponent):

    def th_form(self, form):
        bc = form.center.borderContainer()
        fb = bc.contentPane(region='top',datapath='.record',nodeId='tblinfo_rec').formbuilder(cols=3, border_spacing='4px')
        fb.field('pkgid')
        fb.field('tblid')
        fb.field('description',colspan=3,width='100%')
        tc = bc.tabContainer(region='center',margin='2px',parentForm=False)
        self.qtreeItems(tc.contentPane(title='Quick Fields Tree'))

    def qtreeItems(self,pane):
        frame = pane.multiButtonForm(frameCode='qtree_#',relation='@items',
                                condition='$item_type=:t',
                                condition_t='QTREE',default_item_type='QTREE',
                                caption='description',
                                datapath='#FORM.thqt',
                                #viewResource='QTREEItemView',
                                formResource='QTREEItemForm',
                                multibutton_deleteSelectedOnly=True,multibutton_deleteAction="""
                                var s = this._value.getNode('store').gnrwdg.store;
                                s.deleteAsk([value]);
                            """,
                                margin='3px',border='1px solid silver')
        frame.multiButtonView.item(code='add_it',caption='+',
                                    action='genro.publish("new_qtree",{code:custom_code || standard_code,description:custom_description || description || custom_code,based_on:based_on});',
                                    ask=dict(title='New Item',fields=[dict(lbl='Standard code',
                                                                    name='standard_code',tag='remoteSelect',
                                                                    auxColumns='code,description',
                                                                    method='_table.adm.tblinfo_item.getFilteredOptions',
                                                                    condition_tbl='=#tblinfo_rec.tblid',
                                                                    condition_item_type='QTREE',
                                                                    selected_description='.description',
                                                                    values=self.db.table('adm.user_config').type_QTREE(),
                                                                    hasDownArrow=True),
                                                                dict(lbl='Custom code',
                                                                    name='custom_code',disabled='^.standard_code'), 
                                                                dict(lbl='Custom description',
                                                                    name='custom_description',disabled='^.standard_code'),
                                                                dict(lbl='Based on',
                                                                    name='based_on',tag='dbselect',
                                                                    dbtable='adm.tblinfo_item',condition='$tblid=:tbl AND $item_type=:item_type',
                                                                        condition_tbl='=#tblinfo_rec.tblid',
                                                                        condition_item_type='QTREE')],
                                                               ),
                parentForm=True,deleteAction=False)
        frame.dataRpc(None,self.newTblInfoItem,subscribe_new_qtree=True,
                        tblid='=#FORM.record.tblid',item_type='QTREE',
                    _onResult="SET .value = result;")

    @public_method
    def newTblInfoItem(self,code=None,description=None,based_on=None,item_type=None,tblid=None):
        data = Bag()
        data['root'] = Bag()
        infoitem_tbl = self.db.table('adm.tblinfo_item')
        if based_on:
            data = infoitem_tbl.readColumns(pkey=based_on,columns='$data')
        rec = dict(code=code,description=description,item_type=item_type,tblid=tblid,data=data)
        infoitem_tbl.insert(rec)
        self.db.commit()
        return rec['info_key']

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

