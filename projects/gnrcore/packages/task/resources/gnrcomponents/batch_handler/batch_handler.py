# -*- coding: UTF-8 -*-

# untitled.py
# Created by Francesco Porcari on 2012-04-05.
# Copyright (c) 2012 Softwell. All rights reserved.

from gnr.web.gnrwebpage import BaseComponent
from gnr.core.gnrdecorator import oncalled,public_method
from gnr.core.gnrbag import Bag

class TableScriptRunner(BaseComponent):
    #py_requires='th/th:TableHandler'
    
    def onMain_make_schedulerDialog(self):
        page = self.pageSource()
        self.scheduler_dialog(page)
        
    @oncalled
    def table_script_dialogs(self,pane,batch_dict=None,extra_parameters=None,**kwargs):
        if not self.application.checkResourcePermission(batch_dict.get('plan_tag','admin'),self.userTags):
            return
        hasOptions = hasattr(self, 'table_script_option_pane')
        hasParameters = hasattr(self, 'table_script_parameters_pane')
        pane.data('gnr.dialog_scheduler.pars',Bag(dict(resource_path=batch_dict.get('resource_path'),table=batch_dict.get('table'))))
        if hasOptions:
            return self._scheduler_footer(pane.optionsDialog.footerNode.bar,batch_dict=batch_dict,extra_parameters=extra_parameters)
        if hasParameters:
            return self._scheduler_footer(pane.parametersDialog.footerNode.bar,batch_dict=batch_dict,extra_parameters=extra_parameters)

    def _scheduler_footer(self,bar,batch_dict=None,extra_parameters=None,**kwargs):
        bar.replaceSlots('#','scbtn,#')
        bar.scbtn.slotButton('!!Schedule',action='genro.wdgById("task_common_scheduler_dialog").show(); FIRE gnr.dialog_scheduler.dlg_show;')
    
    def scheduler_dialog(self,pane,extra_parameters=None,resource_path=None,table=None,**kwargs):
        dialog = pane.dialog(title='Scheduler',datapath='gnr.dialog_scheduler',closable=True,nodeId='task_common_scheduler_dialog')
        frame = dialog.framePane(height='510px',width='600px')
        frame.center.contentPane().remote(self._commonTaskTableHandler)
        
    @public_method
    def _commonTaskTableHandler(self,pane):
        th = pane.stackTableHandler(table='task.task',default_command='=gnr.dialog_scheduler.pars.resource_path',
                                    default_table_name='=gnr.dialog_scheduler.pars.table',
                                    default_parameters='=#table_script_runner.data',
                                    default_user_id=self.avatar.user_id)
        th.view.store.attributes.update(where='$command=:rpath AND $table_name=:t',rpath='=gnr.dialog_scheduler.pars.resource_path',
                                        t='=gnr.dialog_scheduler.pars.table',
                                        _fired='^gnr.dialog_scheduler.dlg_show',_onBuilt=True)
        #frame.bottom.slotBar('*,closebtn',_class='slotbar_dialog_footer')
        
    