# -*- coding: UTF-8 -*-

# test_special_action.py
# Created by Francesco Porcari on 2010-07-02.
# Copyright (c) 2011 Softwell. All rights reserved.
from gnr.web.batch.btcbase import BaseResourceBatch
from gnr.core.gnrbag import Bag
from gnr.core.gnrstring import templateReplace
import datetime
import os

caption = 'Dump all'
description = 'Dump all'
tags = 'nobody'
class Main(BaseResourceBatch):
    dialog_height = '450px'
    dialog_width = '650px'
    batch_prefix = 'BU'
    batch_title = 'Dump all'
    batch_cancellable = False
    batch_delay = 0.5
    batch_steps = 'dumpmain,dumpaux,end'

    def pre_process(self):
        self.dumpfolder = self.page.getPreference(path='backups.backup_folder',pkg='adm') or self.page.site.getStaticPath('site:backups')
        self.max_copies = self.page.getPreference(path='backups.max_copies',pkg='adm') or 10
        self.ts_start = datetime.datetime.now()
        self.dump_name = self.batch_parameters['name'] or '%04i_%02i_%02i_%02i_%02i' %(self.ts_start.year,self.ts_start.month,
                                                                                self.ts_start.day,self.ts_start.hour,self.ts_start.minute)
        self.filelist = []

    def step_dumpmain(self):
        """!!Dump main db"""
        fname = os.path.join(self.dumpfolder,self.dump_name,'mainstore')
        self.filelist.append(fname)
        self.db.dump(fname)

    def step_dumpaux(self):
        """!!Dump aux db"""
        for s in self.btc.thermo_wrapper(self.db.stores_handler.dbstores.keys(),line_code='dbl',message='db'):
            with self.db.tempEnv(storename=s):
                fname = os.path.join(self.dumpfolder,self.dump_name,s)
                self.filelist.append(fname)
                self.db.dump(fname)

    def step_end(self):
        self.tblobj.insert(dict(name=self.dump_name,start_ts=self.ts_start,end_ts=datetime.datetime.now()))
        self.db.commit()
        if self.batch_parameters['zipdump']:
            self.page.site.zipFiles(file_list=self.filelist, zipPath=os.path.join(self.dumpfolder,self.dump_name))

    def table_script_parameters_pane(self, pane, **kwargs):
        fb = pane.div(padding='10px').formbuilder(cols=1,border_spacing='3px')
        fb.textbox(value='^.name',lbl='!!Backup name')
        fb.checkbox(value='^.zipdump',label='!!Zip')

