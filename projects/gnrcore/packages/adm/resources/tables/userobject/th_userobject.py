#!/usr/bin/python
# -*- coding: UTF-8 -*-

from gnr.web.gnrbaseclasses import BaseComponent
from gnr.core.gnrdecorator import public_method
from gnr.core.gnrbag import Bag

class View(BaseComponent):
    def th_struct(self,struct):
        r = struct.view().rows()
        r.fieldcell('code',width='10em')
        r.fieldcell('objtype',width='10em')
        r.fieldcell('pkg',width='6em')
        r.fieldcell('tbl',width='10em')
        r.fieldcell('userid',width='6em')
        r.fieldcell('description',width='6em')
        r.fieldcell('notes',width='6em')
        r.fieldcell('authtags',width='6em')
        r.fieldcell('private',width='6em')
        r.fieldcell('flags',width='6em')
        
    def th_order(self):
        return 'code'

    def th_query(self):
        return dict(column='objtype', op='contains', val='')


class Form(BaseComponent):
    def th_form(self, form):
        pane = form.record
        fb = pane.formbuilder(cols=2, border_spacing='4px')
        fb.field('code')
        fb.field('objtype')
        fb.field('pkg')
        fb.field('tbl')
        fb.field('userid')
        fb.field('description')
        fb.field('notes')
        fb.field('authtags')
        fb.field('private')
        fb.field('quicklist')
        fb.field('flags')


    def th_options(self):
        return dict(dialog_height='400px', dialog_width='600px')

class ViewCustomColumn(BaseComponent):
    def th_struct(self,struct):
        r = struct.view().rows()
        r.fieldcell('code',width='10em')
        r.fieldcell('userid',width='6em')
        r.fieldcell('description',width='6em')
        r.fieldcell('notes',width='6em')
        r.fieldcell('authtags',width='6em')
        r.fieldcell('private',width='6em')
        
    def th_order(self):
        return 'code'

    def th_query(self):
        return dict(column='objtype', op='contains', val='')

    def th_condition(self):
        return dict(condition='$tbl=:curr_tbl AND $objtype=:ot',condition_ot='formulacolumn',condition_curr_tbl='=current.tbl')

    def th_options(self):
        return dict(virtualStore=False)

class FormCustomColumn(BaseComponent):

    def th_form(self, form):
        pane = form.record.div(margin_left='10px',margin_right='20px',margin_top='10px')
        fb = pane.formbuilder(cols=2, border_spacing='4px',width='100%',fld_width='100%')
        fb.field('code',validate_notnull=True)
        fb.field('description',validate_notnull=True)
        fb.field('notes',colspan=2)
        fb.field('private',html_label=True)
        fb.filteringSelect(value='^.data.dtype',values='B:Boolean,T:Text,N:Numeric,L:Integer',lbl='!!Data type',validate_notnull=True)
        fb.textbox(value='^.data.fieldname',lbl='!!Field',validate_notnull=True)
        fb.textbox(value='^.data.group',lbl='!!Group')
        fb.simpleTextArea(value='^.data.sql_formula',lbl='Sql',colspan=2,width='100%',height='50px')


    @public_method
    def th_onLoading(self,record, newrecord, loadingParameters, recInfo):
        if newrecord:
            record['userid'] = self.user


    def th_options(self):
        return dict(#newTitleTemplate='!!New custom column',titleTemplate='Column:$code-$description',modal=True,
                    default_objtype='formulacolumn',
                    default_tbl='=current.tbl',
                    default_pkg='=current.pkg',dialog_height='210px',dialog_width='500px')



