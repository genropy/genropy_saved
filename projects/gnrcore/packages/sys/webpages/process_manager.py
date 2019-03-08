#!/usr/bin/env pythonw
# -*- coding: utf-8 -*-
#
#  Created by Francesco Porcari on 2019-03-24.
#  Copyright (c) 2007 Softwell. All rights reserved.
#

from gnr.core.gnrdecorator import public_method
from gnr.core.gnrbag import Bag
import psutil
import datetime
import re


class GnrCustomWebPage(object):
    py_requires="""public:Public"""
    auth_main = '_DEV_'


    def windowTitle(self):
        return '!!Process manager'

    def main(self, root, **kwargs):
        bc = root.rootBorderContainer(title='Process manager manager',datapath='main',design='sidebar')
        self.process_manager(bc.contentPane(region='center'))
    
    def process_manager(self,root,**kwargs):
        properties=['pid','ppid','name','username','status','create_time',
                    'cpu_percent','memory_percent','cwd','nice','uids',
                    'gids','cpu_times','memory_info','exe']
        pane =root.div(margin='15px',datapath='processList')
        pane.h1('Processlist')
        fb=pane.formbuilder(cols=2)
        fb.textBox('^.userName',lbl='User Name')
        fb.textBox('^.processName', lbl='Process Name')
        fb.numberTextBox('^.cpuPerc', lbl='% Cpu')
        fb.numberTextBox('^.memPerc', lbl='% Memory')
        fb.checkBoxText('^.columns',values=','.join(properties),colspan=2,
                        cols=3,
                        width='100%',
                        default_value='pid,name,username,cpu_percent',
                        lbl='Columns',popup=True)
        
        pane.dataRpc('.data', self.getProcessesBag, columns='^.columns',
                             userName='^.userName',processName='^.processName',
                             cpuPerc='^.cpuPerc', memPerc='^.memPerc',
                             _timing=1, _onStart=True)
    
        pane.quickGrid(value='^.data',height='200px',width='auto',
                                      sortedBy='cpu_percent:d',
                                      border='1px solid silver')
        
    @public_method
    def getProcessesBag(self,columns=None, userName=None, 
                        processName=None,memPerc=None,cpuPerc=None):
        columns=(columns or 'pid,name').split(',')
        result = Bag()
        for p in psutil.process_iter():
            d=p.as_dict()
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
    
    