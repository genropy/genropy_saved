#!/usr/bin/python
# -*- coding: UTF-8 -*-

from gnr.web.gnrbaseclasses import BaseComponent
from gnr.core.gnrdecorator import public_method

class View(BaseComponent):

    def th_struct(self,struct):
        r = struct.view().rows()
        r.fieldcell('codekey')
        r.fieldcell('code')
        r.fieldcell('pkg')
        r.fieldcell('tbl')
        r.fieldcell('fld')
        r.fieldcell('counter')
        r.fieldcell('last_used')

    def th_order(self):
        return 'tbl'

    def th_query(self):
        return dict(column='tbl', op='contains', val='')

    def th_sections_pkgsel(self):
        result = []
        f = self.db.table('adm.counter').query(columns='$pkg',distinct=True).fetch()
        if f:
            for r in f:
                pkgId = r['pkg']
                result.append(dict(code=pkgId,caption=pkgId,condition='$pkg=:cpkg',condition_cpkg=pkgId))
        result.append(dict(code='all',caption='All'))
        return result

    def th_sections_errors(self):
        return [dict(code='all',caption='!!All'),
                dict(code='ok',caption='!!Ok',condition='$holes IS NULL AND $errors IS NULL'),
                dict(code='holes',caption='!!Holes',condition='$holes IS NOT NULL'),
                dict(code='duplicates',caption='!!Duplicates',condition='$errors IS NOT NULL AND $errors ILIKE :errtype',condition_errtype='%%duplicates%%'),
                dict(code='wrongOrder',caption='!!Wrong order',condition='$errors IS NOT NULL AND $errors ILIKE :errtype',condition_errtype='%%wrongOrder%%')
                ]


    def th_top_upperslotbar(self,top):
        top.slotToolbar('5,sections@pkgsel,*,sections@errors,5',childname='upper',_position='<bar',gradient_from='#999',gradient_to='#666')

    def th_options(self):
        return dict(addrow=False)

class Form(BaseComponent):

    def th_form(self, form):
        bc = form.center.borderContainer()
        fb = bc.contentPane(region='top',datapath='.record').div(margin_right='30px').formbuilder(cols=3, border_spacing='4px',
                colswidth='auto',fld_width='100%')
        fb.field('codekey',colspan=2)
        fb.field('code')
        fb.field('pkg')
        fb.field('tbl')
        fb.field('fld')
        fb.field('counter')
        fb.field('last_used')
        fb.button('Align',fire='#FORM.alignCounter')
        center = bc.borderContainer(region='center',margin='2px')
        center.contentPane(region='top',height='50%').bagGrid(storepath='#FORM.record.holes',struct=self.holesStruct,
                        pbl_classes=True,title='Holes', margin='2px',addrow=False,delrow=False)
        center.contentPane(region='left',width='50%').bagGrid(storepath='#FORM.record.errors.duplicates',struct=self.duplicatesStruct,
                        pbl_classes=True,title='Duplicates', margin='2px',addrow=False,delrow=False)
        center.contentPane(region='center').bagGrid(storepath='#FORM.record.errors.wrongOrder',struct=self.wrongOrderStruct,
                        pbl_classes=True,title='Wrong order', margin='2px',addrow=False,delrow=False)
        bc.dataRpc('dummy',self.db.table('adm.counter').alignCounter,pkey='=#FORM.record.codekey',_fired='^#FORM.alignCounter',
                    _lockScreen=True,_onResult='this.form.reload();')

    def holesStruct(self,struct):
        r = struct.view().rows()
        r.cell('cnt_from', name='Counter from',dtype='L', width='10em')
        r.cell('cnt_to', name='Counter to',dtype='L', width='10em')
        r.cell('date_from', name='Valid from',dtype='D', width='10em')
        r.cell('date_to', name='Valid to',dtype='D', width='10em')

    def duplicatesStruct(self,struct):
        r = struct.view().rows()
        r.cell('cnt', name='Counter',dtype='L', width='10em')

    def wrongOrderStruct(self,struct):
        r = struct.view().rows()
        r.cell('cnt', name='Counter',dtype='L', width='10em')
        r.cell('cnt_date', name='Counter date',dtype='D', width='10em')
        r.cell('prev_date', name='Prev. cnt. date',dtype='D', width='10em')


    def th_options(self):
        return dict(dialog_height='400px', dialog_width='600px',readOnly=True)
