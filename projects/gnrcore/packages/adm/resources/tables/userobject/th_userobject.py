# -*- coding: UTF-8 -*-

from gnr.web.gnrbaseclasses import BaseComponent
from gnr.core.gnrdecorator import public_method
from gnr.core.gnrbag import Bag

class View(BaseComponent):
    def th_hiddencolumns(self):
        return '$data'

    def th_struct(self,struct):
        r = struct.view().rows()
        r.fieldcell('code',width='10em')
        r.fieldcell('objtype',width='10em')
        r.fieldcell('pkg',width='6em')
        r.fieldcell('tbl',width='20em')
        r.fieldcell('userid',width='6em')
        r.fieldcell('description',width='20em')
        r.fieldcell('authtags',width='6em')
        r.fieldcell('private',width='6em')
        r.fieldcell('flags',width='6em')
        r.fieldcell('required_pkg',width='10em')
        r.fieldcell('__mod_ts',name='Local modTS',width='10em')
        r.fieldcell('resource_status',width='20em')

        if self.isDeveloper():
            r.cell('save_as_resource',calculated=True,format_buttonclass='buttonInGrid',
                        format_isbutton='!!Make resource',
                        format_onclick="""PUBLISH save_uo_as_resource = {pkeys:this.widget.getSelectedPkeys().length? this.widget.getSelectedPkeys():[this.widget.rowByIndex($1.rowIndex)['_pkey']]};""",
                        name=' ',width='10em')

    def th_order(self):
        return 'code'

    def th_options(self):
        return dict(virtualStore=False,addrow=False)

    def th_view(self,view):
        view.dataRpc(None,self.db.table('adm.userobject').saveAsResource,
                        subscribe_save_uo_as_resource=True,
                       _if='pkeys',_onResult='FIRE .runQueryDo;',
                        _lockScreen=True)
    
    def th_condition(self):
        return dict(condition="$system_userobject IS NOT TRUE")

    
    def th_top_custom(self,top):
        top.slotToolbar('2,sections@packages,*,sections@types',childname='upper',_position='<bar')

    def th_sections_packages(self):
        return self.th_distinctSections(table='adm.userobject',field='pkg')

    def th_sections_types(self):
        return self.th_distinctSections(table='adm.userobject',field='objtype')

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



