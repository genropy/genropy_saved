#!/usr/bin/python
# -*- coding: utf-8 -*-

from gnr.web.gnrbaseclasses import BaseComponent
from gnr.core.gnrdecorator import public_method
from gnr.core.gnrbag import Bag

class View(BaseComponent):

    def th_struct(self,struct):
        r = struct.view().rows()
        r.fieldcell('tablename')
        r.fieldcell('username')
        r.fieldcell('record_pkey')
        r.fieldcell('version')
        r.fieldcell('transaction_id')

    def th_order(self):
        return 'tablename'

    def th_query(self):
        return dict(column='tablename', op='contains', val='')

class ViewRecordHistory(BaseComponent):
    def th_hiddencolumns(self):
        return '$event,$data'

    def th_struct(self,struct):
        r = struct.view().rows()
        r.fieldcell('version',name='V',width='4em')
        r.fieldcell('__ins_ts',name='TS',width='10em')
        r.fieldcell('username',name='User',width='10em')
        r.cell('changed_fields',name='Changes',width='15em',calculated=True)


    @public_method
    def th_applymethod(self,selection):
        selection.sort('version') 
        self._curr_audit_record = Bag()
        def cb(row):
            b = Bag(row['data'])
            result = dict()
            if row['version'] >0:
                result['changed_fields'] = '<br/>'.join(list(b.keys()))
            b.pop('__ins_ts')
            b.pop('__version')
            b.pop('__mod_ts')
            self._curr_audit_record.update(b)
            result['__value__'] = self._curr_audit_record.deepcopy()
            return result
        selection.apply(cb)
        selection.sort('version:d') 

    def th_order(self):
        return 'version:d'

    def th_query(self):
        return dict(column='tablename', op='contains', val='')



class Form(BaseComponent):

    def th_form(self, form):
        pane = form.record
        fb = pane.formbuilder(cols=2, border_spacing='4px')
        fb.field('tablename')
        fb.field('event')
        fb.field('username')
        fb.field('record_pkey')
        fb.field('version')
        fb.field('data')
        fb.field('transaction_id')



    def th_options(self):
        return dict(dialog_height='400px', dialog_width='600px')

class FormRecordHistory(BaseComponent):
    def th_top_custom(self,top):
        bar = top.bar.replaceSlots('#','10,applyOnRecord,*')
        bar.applyOnRecord.slotButton('Apply',
                                    action="this.form.getParentForm().updateFormData(recordAtVersion);",
                                    recordAtVersion='=#FORM.recordAtVersion')



    def th_form(self, form):
        tc = form.center.tabContainer(margin='2px')
        tc.contentPane(title='Changes',datapath='.record',overflow='hidden').multiValueEditor(value='^#FORM.record.data',readOnly=True,margin='2px')
        tc.contentPane(title='Record at version',overflow='hidden').multiValueEditor(value='^#FORM.recordAtVersion',readOnly=True,margin='2px')
        form.dataController("""var v = this.form.store.parentStore.getData().getNodeByAttr('_pkey',this.form.getCurrentPkey()).getValue()
                              SET #FORM.recordAtVersion = v?v.deepCopy():null;""",_fired='^.controller.loaded')

