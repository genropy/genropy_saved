# -*- coding: UTF-8 -*-

# untitled.py
# Created by Francesco Porcari on 2012-04-05.
# Copyright (c) 2012 Softwell. All rights reserved.

from gnr.web.gnrwebpage import BaseComponent
from gnr.core.gnrdecorator import oncalled

class TableScriptRunner(BaseComponent):
    py_requires='th/th:TableHandler'
    @oncalled
    def table_script_dialogs(self,pane,batch_dict=None,extra_parameters=None,**kwargs):
        if not self.application.checkResourcePermission(batch_dict.get('plan_tag','admin'),self.userTags):
            return
        hasOptions = hasattr(self, 'table_script_option_pane')
        hasParameters = hasattr(self, 'table_script_parameters_pane')
        if hasOptions:
            return self._scheduler_footer(pane.optionsDialog.footerNode.bar,batch_dict=batch_dict,extra_parameters=extra_parameters)
        if hasParameters:
            return self._scheduler_footer(pane.parametersDialog.footerNode.bar,batch_dict=batch_dict,extra_parameters=extra_parameters)

    def _scheduler_footer(self,bar,batch_dict=None,extra_parameters=None,**kwargs):
        bar.replaceSlots('#','scbtn,#')
        dialog = self.scheduler_dialog(bar,extra_parameters=extra_parameters,**batch_dict)
        bar.scbtn.slotButton('!!Schedule',action='dialog.show(); FIRE gnr.dialog_scheduler.dlg_show;',dialog=dialog.js_widget)
    
    def scheduler_dialog(self,pane,extra_parameters=None,resource_path=None,table=None,**kwargs):
        dialog = pane.dialog(title='Scheduler',datapath='gnr.dialog_scheduler',closable=True)
        frame = dialog.framePane(height='510px',width='600px')
        th = frame.stackTableHandler(table='task.task',default_command=resource_path,
                                    default_table_name=table,default_user_id=self.avatar.user_id)
        th.view.store.attributes.update(_fired='^gnr.dialog_scheduler.dlg_show')
        #frame.bottom.slotBar('*,closebtn',_class='slotbar_dialog_footer')
        return dialog
        
    