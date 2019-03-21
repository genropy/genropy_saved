#!/usr/bin/env pythonw
# -*- coding: utf-8 -*-
#
#  Created by Francesco Porcari on 2019-04-06.
#  Copyright (c) 2019 Softwell. All rights reserved.

import xmlrpclib
import datetime
from gnr.core.gnrdecorator import public_method
from gnr.core.gnrbag import Bag
from gnr.web.gnrbaseclasses import BaseComponent

from gnrpkg.sys.services.instancemonitor import InstanceMonitorService

class Service(InstanceMonitorService):
    def __init__(self, parent=None,host=None,username=None,password=None,port=None,**kwargs):
        self.parent = parent
        self.proxy_kwargs = dict(host=host, username=username, password=password, port=port)
        if host:
            self.proxy = xmlrpclib.ServerProxy('http://%(username)s:%(password)s@%(host)s:%(port)s/RPC2' %self.proxy_kwargs)

    def getAllProcessInfo(self):
        if hasattr(self,'proxy'):
            return self.proxy.supervisor.getAllProcessInfo()
        return []

class ServiceParameters(BaseComponent):

    def service_parameters(self,pane,datapath=None,**kwargs):
        bc = pane.borderContainer()
        fb = bc.contentPane(region='top').formbuilder(datapath=datapath,cols=4)
        fb.textbox(value='^.host',lbl='Host')
        fb.textbox(value='^.username',lbl='Username')
        fb.textbox(value='^.password',lbl='Password',type='password')
        fb.textbox(value='^.port',lbl='Port')
        center = bc.borderContainer(region='center',nodeId='supervisordProcessMonitor',_workspace=True)
        frame = center.contentPane(region='center',datapath='#WORKSPACE.allprocess').bagGrid(frameCode='supervisordProcess',
                                                    struct=self.supervisord_process_struct,
                                                    storepath='#WORKSPACE.allprocess.store',
                                                    store_selfUpdate=True,
                                                    store_data='^#WORKSPACE.allprocess.storeresult',
                                                    addrow=False,delrow=False,datamode='attr')
        bar = frame.top.bar.replaceSlots('#','2,vtitle,2,refresh,timerslot,*,searchOn,5')
        bar.vtitle.div('Process monitor')
        bar.timerslot.formbuilder(border_spacing='0').numberTextBox(value='^.timing',lbl='Timing',width='4em')
        bar.dataFormula('.timing','timing',timing=3,_onBuilt=1)

        frame.dataRpc('#WORKSPACE.allprocess.storeresult',self.spd_allProcessInfo,service_name='^#FORM.record.service_name',
                        _if='service_name',_onBuilt=True,_timing='^.timing')
    
    @public_method
    def spd_allProcessInfo(self,service_name=None,**kwargs):
        result = Bag()
        for p in self.site.getService('instancemonitor',service_name).getAllProcessInfo():
            row = {}
            for k in ('group','pid','name','statename','description'):
                row[k] = p[k]
            row['pid'] = str(row['pid'])
            row['uptime'] = p['now']-p['start']
            row['_pkey'] = 'p_%(pid)s' %row
            row['uptime_desc'] = str(datetime.timedelta(seconds=row['uptime']))
            result.setItem('p_%(pid)s' %row,None,row)

        return result

    def supervisord_process_struct(self,struct):
        r=struct.view().rows()
        r.cell('group',name='Group',width='12em')
        r.cell('name',name='Name',width='20em')
        r.cell('pid',name='Pid',width='8em')
        r.cell('statename',name='Status',width='12em')
        r.cell('uptime_desc',name='Uptime',width='12em')
        r.cell('description',name='Description',width='20em')
