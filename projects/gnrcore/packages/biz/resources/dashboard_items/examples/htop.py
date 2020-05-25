# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------
# Copyright (c) : 2004 - 2020 Softwell sas - Milano 
# Written by    : Giovanni Porcari, Michele Bertoldi
#                 Saverio Porcari, Francesco Porcari
#--------------------------------------------------------------------------
#This library is free software; you can redistribute it and/or
#modify it under the terms of the GNU Lesser General Public
#License as published by the Free Software Foundation; either
#version 2.1 of the License, or (at your option) any later version.

#This library is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
#Lesser General Public License for more details.

#You should have received a copy of the GNU Lesser General Public
#License along with this library; if not, write to the Free Software
#Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA


from gnrpkg.biz.dashboard import BaseDashboardItem
from gnr.core.gnrdecorator import public_method
from gnr.core.gnrbag import Bag
import psutil
import datetime


caption = 'Dashboard htop'
description = 'Dashboard process viewer'
objtype = 'dash_example_htop'
item_parameters = []


class Main(BaseDashboardItem):
    title_template = 'Processi del server'

    def content(self,pane, table=None,**kwargs):
        bc = pane.borderContainer()
        top =bc.contentPane(region='top', datapath='.filters')
        
        fb=top.formbuilder(cols=4, fld_width='6em')
        fb.textBox('^.userName',lbl='User Name')
        fb.textBox('^.processName', lbl='Process Name')
        fb.numberTextBox('^.cpuPerc', lbl='% Cpu')
        fb.numberTextBox('^.memPerc', lbl='% Memory')

        center = bc.contentPane(region='center')
        center.dataRpc('.data', self.getProcessesBag, 
                            columns='^.conf.columns',
                             userName='^.filters.userName', processName='^.filters.processName',
                             cpuPerc='^.filters.cpuPerc', memPerc='^.filters.memPerc',
                             _timing='^.conf.timing', 
                             _onStart=True)

        center.quickGrid(value='^.data',height='200px',width='500px',
                                      sortedBy='cpu_percent:d',
                                      border='1px solid silver')


    def configuration(self,pane,**kwargs):
        properties=['pid','ppid','name','username','status','create_time',
                    'cpu_percent','memory_percent','cwd','nice','uids',
                    'gids','cpu_times','memory_info','exe']
        #pane = pane.div(margin='15px',datapath='processList')
        #pane.h1('Processlist')
        fb=pane.formbuilder(cols=1)
        fb.numberSpinner('^.timing', lbl='Refresh time', default=1, width='5em')
        fb.checkBoxText('^.columns',values=','.join(properties),colspan=2,
                        cols=3,
                        width='100%',
                        default_value='pid,name,username,cpu_percent',
                        lbl='Columns')

          

    @public_method
    def getProcessesBag(self,columns=None, userName=None, 
                        processName=None,memPerc=None,cpuPerc=None):
        columns=(columns or 'status').split(',')
        result = Bag()
        for p in psutil.process_iter():
            try:
                d=p.as_dict()
            except Exception as e:
                continue
            if userName and not  userName.lower() in d['username'].lower():
                continue
            if processName and not processName.lower() in d['name'].lower():
                continue
            d['create_time'] = datetime.datetime.fromtimestamp(d['create_time'])
            d['cpu_percent'] = d['cpu_percent'] or 0. 
            d['memory_percent'] = d['memory_percent'] or 0.
            if memPerc and d['memory_percent'] < memPerc:
                continue
            if cpuPerc and d['cpu_percent']<cpuPerc:
                continue
            row = Bag([(k,d[k]) for k in columns if k in d])
            result.setItem('p_%s'%p.pid,row)
        return result
    
    