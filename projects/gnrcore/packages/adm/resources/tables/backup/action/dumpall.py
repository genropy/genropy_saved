# -*- coding: UTF-8 -*-

# test_special_action.py
# Created by Francesco Porcari on 2010-07-02.
# Copyright (c) 2011 Softwell. All rights reserved.
from gnr.web.batch.btcbase import BaseResourceBatch
from gnr.core.gnrbag import Bag
from gnr.core.gnrstring import templateReplace
import datetime
import os
import shutil

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
        self.dumpfolder = self.page.getPreference(path='backups.backup_folder',pkg='adm') or 'site:maintenance'
        dumpfolderpath = self.page.site.getStaticPath(self.dumpfolder,'backups',autocreate=-1)
        self.max_copies = self.page.getPreference(path='backups.max_copies',pkg='adm') or 10
        self.ts_start = datetime.datetime.now()
        self.dump_name = self.batch_parameters['name'] or '%04i_%02i_%02i_%02i_%02i' %(self.ts_start.year,self.ts_start.month,
                                                                                self.ts_start.day,self.ts_start.hour,self.ts_start.minute)
        self.folderpath = os.path.join(dumpfolderpath,self.dump_name)
        os.makedirs(self.folderpath)
        self.filelist = []
        self.dump_rec = dict(name=self.dump_name,start_ts=self.ts_start)
        self.tblobj.insert(self.dump_rec)


    def step_dumpmain(self):
        """Dump main db"""
        fname = os.path.join(self.folderpath,'mainstore')
        self.filelist.append(fname)
        self.db.dump(fname,extras=self.getExcluded())

    def step_dumpaux(self):
        """Dump aux db"""
        for s in self.btc.thermo_wrapper(self.db.stores_handler.dbstores.keys(),line_code='dbl',message=lambda item, k, m, **kwargs: 'Dumping %s' %item):
            with self.db.tempEnv(storename=s):
                fname = os.path.join(self.folderpath,s)
                self.filelist.append(fname)
                self.db.dump(fname,dbname=self.db.stores_handler.dbstores[s]['database'],extras=self.getExcluded())

    def getExcluded(self):
        checked = self.batch_parameters['dumppackages'].split(',')
        result = []
        for k in self.db.packages.keys():
            if not k in checked:
                result.append('-N')
                result.append(k)
        return result


    def step_end(self):
        oldrec = dict(self.dump_rec)
        self.dump_rec.update(end_ts=datetime.datetime.now())
        self.tblobj.update(self.dump_rec,old_record=oldrec)
        self.db.commit()
        self.zipPath='%s.zip' %self.folderpath
        self.page.site.zipFiles(file_list=self.filelist, zipPath=self.zipPath)
        shutil.rmtree(self.folderpath)

    def result_handler(self):
        resultAttr = dict(url=self.page.site.getStaticUrl(self.dumpfolder,'backups','%s.zip' %self.dump_name))
        return 'Dump complete', resultAttr

    def table_script_parameters_pane(self, pane, **kwargs):
        fb = pane.div(padding='10px').formbuilder(cols=1,border_spacing='3px')
        fb.textbox(value='^.name',lbl='!!Backup name')
        values = []
        defaultchecked = []
        for k,v in self.db.packages.items():
            if not v.attributes.get('dump_exclude'):
                defaultchecked.append(k)
            values.append('%s:%s,/' %(k,v.attributes.get('name_long',k)))
        fb.data('.dumppackages',','.join(defaultchecked))
        fb.checkBoxText(value='^.dumppackages',values=','.join(values))






