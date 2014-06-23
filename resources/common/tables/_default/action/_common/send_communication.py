# -*- coding: UTF-8 -*-

# test_special_action.py
# Created by Francesco Porcari on 2010-07-02.
# Copyright (c) 2011 Softwell. All rights reserved.

from gnr.web.batch.btcaction import BaseResourceAction

caption = 'Send communication'
tags = 'user'
description = 'Send communication'

class Main(BaseResourceAction):
    batch_prefix = 'cm'
    batch_title = 'Send communication'
    batch_cancellable = False
    batch_delay = 0.5
    batch_immediate = True
    
    def table_script_parameters_pane(self, pane, table=None,**kwargs):
        tblobj = self.db.table(table)
        if not hasattr(tblobj,'communication_quicksender'):
            pane.div('!!Missing Communication fields',padding='20px')
        fp = pane.framePane(height='200px',width='300px')
        bar = fp.top.slotToolbar('*,communications,*')
        cdict = tblobj.communication_quicksender()
        buttons = []
        availableCommunications = []
        if self.getService('mail'):
            availableCommunications.append(('email','Email'))
        if self.getService('sms'):
            availableCommunications.append(('mobile','Sms'))
        if self.getService('fax'):
            availableCommunications.append(('fax','Fax'))
        for c,lbl in availableCommunications:
            if c in cdict:
                buttons.append('%s:%s' %(c,lbl))
        bar.communications.multiButton(values='!!%s' %','.join(buttons),value='^.communication')
        fp.center.simpleTextArea(value='^.message')

    def do(self):
        if not (hasattr(self.tblobj,'communication_quicksender') and self.batch_parameters.get('message')) :
            return
        cdict = self.tblobj.communication_quicksender()
        selection = self.get_selection(columns='*,%s' %','.join(cdict.values()))
        message = self.batch_parameters['message']
        communication_type = self.batch_parameters['communication']
        communication_field = cdict.get(communication_type)
        for r in self.btc.thermo_wrapper(selection.data,message='Message'):
            cvalue = r.get(communication_field.replace('$',''))
            if cvalue:
                self.page.quickCommunication(message=message,**{'%s'%communication_type:cvalue})

