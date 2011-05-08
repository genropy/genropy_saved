#!/usr/bin/env python
# encoding: utf-8
"""
Created by Softwell on 2008-07-10.
Copyright (c) 2008 Softwell. All rights reserved.
"""

# --------------------------- GnrWebPage Standard header ---------------------------
class GnrCustomWebPage(object):
    maintable = 'adm.authorization'
    py_requires = 'public:Public,standard_tables:TableHandlerLight'

    ######################## STANDARD TABLE OVERRIDDEN METHODS ###############
    def windowTitle(self):
        return '!!Authorization'

    def pageAuthTags(self, method=None, **kwargs):
        return 'admin'

    def tableWriteTags(self):
        return 'admin'

    def tableDeleteTags(self):
        return 'admin'

    def barTitle(self):
        return '!!Authorization'

    def lstBase(self, struct):
        r = struct.view().rows()
        r.fieldcell('@user_id.username', width='15em', name='!!Created by')
        r.fieldcell('note', width='30em')
        r.fieldcell('code', width='6em')

        r.fieldcell('remaining_usages', name='Remaining', width='8em')
        r.fieldcell('expiry_date', name='Exp date', width='8em')
        r.fieldcell('used_by', name='Used by', width='8em')
        r.fieldcell('use_ts', name='Used on', width='8em')
        return struct

    def orderBase(self):
        return '@user_id.username'

    def conditionBase__(self):
        return ('$use_ts IS NULL', {})

    ############################## FORM METHODS ##################################

    def formBase(self, parentBC, disabled=False, **kwargs):
        pane = parentBC.contentPane(**kwargs)
        pane.dataFormula('edit_disabled', '!newrecord', newrecord='^form.record?_newrecord')
        fb = pane.formbuilder(cols=1, border_spacing='4px', disabled=disabled)
        fb.textbox(value='^.code', lbl='!!Code', font_size='2em', readOnly='^edit_disabled')
        fb.simpleTextArea(value='^.note', lbl='!!Note', height='10ex', width='100%')
        fb.field('adm.authorization.remaining_usages', lbl='Max usages')
        fb.field('adm.authorization.expiry_date', lbl='Exp date')

    def onLoading(self, record, newrecord, loadingParameters, recInfo):
        if newrecord:
            record['code'] = self.tblobj.generate_code()

    def onSaving(self, recordCluster, recordClusterAttr, resultAttr):
        recordCluster['user_id'] = self.userRecord('id')
        