#!/usr/bin/python
# -*- coding: utf-8 -*-

from gnr.web.gnrbaseclasses import BaseComponent
from gnr.core.gnrdecorator import public_method

class View(BaseComponent):

    def th_struct(self,struct):
        r = struct.view().rows()
        r.fieldcell('code')
        r.fieldcell('description')
        r.fieldcell('company_code')
        r.fieldcell('customer_id')

    def th_order(self):
        return 'code'

    def th_query(self):
        return dict(column='code', op='contains', val='')


class ViewFromCustomer(BaseComponent):
    def th_struct(self,struct):
        r = struct.view().rows()
        r.fieldcell('code')
        r.fieldcell('description')

    def th_order(self):
        return 'code'

    def th_query(self):
        return dict(column='code', op='contains', val='')

class ViewFromCompany(BaseComponent):
    def th_struct(self,struct):
        r = struct.view().rows()
        r.fieldcell('code')
        r.fieldcell('description')

    def th_order(self):
        return 'code'

    def th_query(self):
        return dict(column='code', op='contains', val='')




class Form(BaseComponent):

    def th_form(self, form):
        bc = form.center.borderContainer()
        fb = bc.contentPane(region='top',datapath='.record').formbuilder(cols=3, border_spacing='10px')
        fb.field('code')
        fb.field('description')
        fb.field('company_code')
        fb.checkBoxText(value='^.languages',lbl='Languages',table='adm.language',cols=4,colspan=3)
        tc = bc.tabContainer(region='center',margin='2px')
        tc.contentPane(title='!!Packages').dialogTableHandler(relation='@packages',viewResource='ViewFromProject',
                                                                formResource='FormFromProject',pbl_classes=True,margin='2px')
        self.localizationGrid(tc.contentPane(title='!!Localization'))
        tc.contentPane(title='!!Tickets').dialogTableHandler(relation='@tickets',pbl_classes=True,margin='2px') #viewResource='ViewFromProject',formResource='FormFromProject

    def localizationGrid(self,pane):
        view = pane.bagGrid(storepath='#FORM.record.localizations',
                            datapath='#FORM.project_localization',
                            struct=self.localizationStruct,title='Localization data',
                            grid_excludeListCb="""
                            var result = [];
                            var packages = this.getRelativeData('.packages');
                            var selected_package= this.getRelativeData('.selected_package');
                            if (selected_package && packages){
                                packages.forEach(function(n){
                                    var pid= n.attr['package_identifier'];
                                    if(selected_package!=pid){
                                        result.push(pid)
                                    }
                                },'static');
                            }
                            return result;
                            """,
                            grid_excludeCol='_package_identifier',
                            margin='2px',rounded=6,border='1px solid silver',
                            addrow=False)
        bar = view.top.bar.replaceSlots('vtitle','mbpackages')
        bar.replaceSlots('delrow','searchOn,delrow')
        mb = bar.mbpackages.multiButton(value='^#FORM.project_localization.selected_package',caption='code')
        mb.store(table='uke.package',condition='$project_code=:pcode',pcode='^#FORM.record.code',
                        storepath='#FORM.project_localization.packages')
        view.dataController("""SET .grid.struct?_counter=genro.getCounter();
                              """,languages='^#FORM.record.languages',grid=view.grid,_delay=100)
        view.dataController("""var deletedRows = grid.gridEditor.deletedRows;
                if(deletedRows){
                    SET #FORM.record.localizations_deleted = deletedRows.keys();
                }
            """,grid=view.grid.js_widget,_fired='^#FORM.controller.saving')
        view.dataController("""
            grid.filterToRebuild(true);
            grid.updateRowCount('*');
            """,package_identifier='^#FORM.project_localization.selected_package',
                    grid=view.grid.js_widget,_if='package_identifier')

    def localizationStruct(self,struct):
        r = struct.view().rows()
        r.cell('_key',name='Key',width='20em')
        for rec in self.db.table('adm.language').query().fetch():
            r.cell(rec['code'],name=rec['name'],width='20em',edit=True,hidden='^#FORM.record.languages?=!#v || #v.indexOf("%s")<0' %rec['code'])


    @public_method
    def th_onLoading(self,record,newrecord,loadingParameters,recInfo):
        if not newrecord:
            localizations = self.db.table('uke.localization').getProjectLocalizations(record['code'])
            record.setItem('localizations',localizations) #_sendback=True


    @public_method
    def th_onSaving(self, recordCluster,recordClusterAttr, resultAttr=None):
        localizations = recordCluster.pop('localizations')
        localizations_deleted = recordCluster.pop('localizations_deleted')
        if localizations or localizations_deleted:
            localizationTable = self.db.table('uke.localization')
            for n in [n for n in localizations.nodes if n.value.filter(lambda j: '__old' in j.attr)]:
                with localizationTable.recordToUpdate(n.label) as rec:
                    v = n.value
                    v.popNode('_key')
                    rec['localization_values'] = v
            if localizations_deleted:
                localizationTable.deleteSelection(where='$id IN :pk',pk=localizations_deleted)

    def th_options(self):
        return dict(dialog_height='400px', dialog_width='600px')

class FormFromCustomer(BaseComponent):

    def th_form(self, form):
        pane = form.record
        fb = pane.formbuilder(cols=2, border_spacing='4px')
        fb.field('code')
        fb.field('description')


    def th_options(self):
        return dict(dialog_height='400px', dialog_width='600px')

class FormFromCompany(BaseComponent):

    def th_form(self, form):
        pane = form.record
        fb = pane.formbuilder(cols=2, border_spacing='4px')
        fb.field('code')
        fb.field('description')

    def th_options(self):
        return dict(dialog_height='400px', dialog_width='600px')
