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
        r.cell('record_count',calculated=True,width='6em',name='Count',dtype='L',format='#,###')

    def th_top_custom(self,top):
        bar = top.bar.replaceSlots('searchOn','5,count_tblrec,5,searchOn')
        bar.count_tblrec.slotButton('Count records',fire='.count_records')
        bar.dataRpc(None,self.countTblinfoRecords,pkgid='=#FORM.record.pkgid',_fired='^.count_records')

    def th_view(self,view):
        view.dataController("""
            store.getNodeByAttr('tblid',tblid).updAttributes({record_count:count});
        """,
        subscribe_update_tblinfo_record_count=True,store='=.store',grid=view.grid.js_widget)
    
    @public_method
    def countTblinfoRecords(self,pkgid=None):
        f = self.db.table('adm.tblinfo').query(where='$pkgid=:pid',pid=pkgid).fetch()
        for r in f:
            tblid = r['tblid']
            self.clientPublish('update_tblinfo_record_count',tblid=tblid,count=self.db.table(tblid).countRecords())


    def th_order(self):
        return 'tblid'


class Form(BaseComponent):

    def th_form(self, form):
        bc = form.center.borderContainer()
        fb = bc.contentPane(region='top',datapath='.record',nodeId='tblinfo_rec').formbuilder(cols=3, border_spacing='4px')
        fb.field('pkgid')
        fb.field('tblid')
        fb.field('description',colspan=3,width='100%')
        tc = bc.tabContainer(region='center',margin='2px',parentForm=False)
        self.congTreeItems(tc.contentPane(title='Quick Fields Tree'),'QTREE')
        self.congTreeItems(tc.contentPane(title='Full Fields Tree'),'FTREE')

    def congTreeItems(self,pane,item_type):
        frame = pane.multiButtonForm(frameCode='conf_tree_%s' %item_type.lower(),relation='@items',
                                condition='$item_type=:t',
                                condition_t=item_type,default_item_type=item_type,
                                caption='description',
                                datapath='#FORM.th_%s' %item_type,
                                #viewResource='QTREEItemView',
                                formResource='ConfTreeItemForm',
                                multibutton_deleteSelectedOnly=True,multibutton_deleteAction="""
                                var s = this._value.getNode('store').gnrwdg.store;
                                s.deleteAsk([value]);
                            """,
                                margin='3px',border='1px solid silver')
        frame.multiButtonView.item(code='add_it',caption='+',
                                    action='FIRE .new_item = {code:custom_code || standard_code,description:custom_description || description || custom_code,based_on:based_on};',
                                    ask=dict(title='New Item',fields=[dict(lbl='Standard code',
                                                                    name='standard_code',tag='remoteSelect',
                                                                    auxColumns='code,description',
                                                                    method='_table.adm.tblinfo_item.getFilteredOptions',
                                                                    condition_tbl='=#tblinfo_rec.tblid',
                                                                    condition_item_type=item_type,
                                                                    selected_description='.description',
                                                                    values=getattr(self.db.table('adm.user_config'),'type_%s' %item_type)(),
                                                                    hasDownArrow=True),
                                                                dict(lbl='Custom code',
                                                                    name='custom_code',disabled='^.standard_code'), 
                                                                dict(lbl='Custom description',
                                                                    name='custom_description',disabled='^.standard_code'),
                                                                dict(lbl='Based on',
                                                                    name='based_on',tag='dbselect',
                                                                    dbtable='adm.tblinfo_item',condition='$tblid=:tbl AND $item_type=:item_type',
                                                                        condition_tbl='=#tblinfo_rec.tblid',
                                                                        condition_item_type=item_type)],
                                                               ),
                parentForm=True,deleteAction=False)
        bar = frame.top.bar.replaceSlots('#','#,cancel_btn,5,save_btn,5')
        bar.cancel_btn.slotButton('!!Undo',action="frm.reload();",frm=frame.form.js_form,iconClass='iconbox revert')
        bar.save_btn.slotButton('!!Apply',action="frm.save();",frm=frame.form.js_form,iconClass='iconbox save')
        frame.dataRpc(None,self.newTblInfoItem,subscribe_new_qtree=True,
                        new_item='^.new_item',
                        tblid='=#FORM.record.tblid',item_type=item_type,
                    _onResult="SET .value = result;")

    @public_method
    def newTblInfoItem(self,new_item=None,tblid=None,item_type=None,**kwargs):
        data = Bag()
        data.setItem('root', Bag(),caption=self.db.table(tblid).name_long)
        infoitem_tbl = self.db.table('adm.tblinfo_item')
        based_on = new_item.pop('based_on')
        if based_on:
            data = infoitem_tbl.readColumns(pkey=based_on,columns='$data')
        new_item['data'] = data
        new_item['tblid'] = tblid
        new_item['item_type'] = item_type
        infoitem_tbl.insert(new_item)
        self.db.commit()
        return new_item['info_key']

    def th_options(self):
        return dict(dialog_parentRatio=0.9)

class FormFromTH(Form):
    def th_form(self, form):
        tc = form.center.tabContainer(margin='3px')
        self.congTreeItems(tc.contentPane(title='Quick Fields Tree'),'QTREE')
        self.congTreeItems(tc.contentPane(title='Full Fields Tree'),'FTREE')

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

