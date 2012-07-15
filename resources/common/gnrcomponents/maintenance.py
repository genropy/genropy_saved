# -*- coding: UTF-8 -*-

# chat_component.py
# Created by Francesco Porcari on 2010-09-08.
# Copyright (c) 2011 Softwell. All rights reserved.

from gnr.web.gnrbaseclasses import BaseComponent
from gnr.core.gnrdecorator import public_method

class MaintenancePlugin(BaseComponent):
    def mainLeft_maintenance(self, pane):
        """!!Maintenance"""
        frame = pane.framePane(datapath='gnr.datamover')
        bc = frame.center.borderContainer()
        top = bc.contentPane(region='top',_class='pbl_roundedGroup',margin='2px')
        top.div('!!Backups',_class='pbl_roundedGroupLabel')
        fb = top.formbuilder(cols=1,border_spacing='3px')
        fb.button('Complete Backup',action='PUBLISH table_script_run = {res_type:"action",resource:"dumpall",table:"adm.backup"};')
        
        
        
                        