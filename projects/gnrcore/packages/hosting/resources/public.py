#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#
#  public.py
#
#  Created by Giovanni Porcari on 2007-03-24.
#  Copyright (c) 2007 Softwell. All rights reserved.

""" public multidb """

from gnr.web.gnrbaseclasses import BaseComponent
from gnr.core.gnrdecorator import public_method


class TableHandlerMain(BaseComponent):
    def onMain_hosting_addOn(self):
        synctables = self.application.config.getItem('packages.gnrcore:hosting.synctables')
        if not synctables:
            return
        r = filter(lambda r: r[0]==self.maintable,synctables.digest('#a.tbl,#a.permission'))
        if not r:
            return
        tbl,permission = r[0]
        th = getattr(self,'root_tablehandler',None)
        if th:
            self.__viewCustomizationHosting(th.view)
    

    def __viewCustomizationHosting(self,view): #poi ci passo il th direttamente
        bar = view.top.slotToolbar('5,htitle,*,hosting_propagate,5',childname='host',_position='<bar',htitle='Hosting bar')        
        bar.hosting_propagate.slotButton('!!Hosting propagate',iconClass='iconbox globe',disabled='^.disabledButton',action='FIRE .hostingDialog')
        bar.dataController("""genro.dlg.prompt(t,{remote:rc},function(result){});
            """,_fired='^.hostingDialog',t='!!Hosted instance',rc=self.hostedInstanceDialogContent)

    @public_method
    def hostedInstanceDialogContent(self,pane,**kwargs):
        box = pane.div(**kwargs).formbuilder(cols=1,border_spacing='3px')
        #instances

    @public_method
    def hostedInstanceFill(self,instance_pkeys=None):
        pass
            