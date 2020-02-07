# -*- coding: utf-8 -*-

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
        self.dump_name = self.batch_parameters['name'] or '%s_%04i%02i%02i_%02i%02i' %(self.db.dbname,self.ts_start.year,self.ts_start.month,
                                                                                self.ts_start.day,self.ts_start.hour,self.ts_start.minute)
        self.folderpath = os.path.join(dumpfolderpath,self.dump_name)
        
        if os.path.exists(self.folderpath):
            shutil.rmtree(self.folderpath)
        #self.folderurl = self.page.site.getStaticUrl(self.dumpfolder,'backups',self.dump_name)
        os.makedirs(self.folderpath)
        self.filelist = []
        self.dump_rec = dict(name=self.dump_name,start_ts=self.ts_start)
        self.tblobj.insert(self.dump_rec)


    def step_dumpmain(self):
        """Dump main db"""
        options = self.batch_parameters['options']
        if not options.get('storeonly'):
            self.filelist.append(self.db.dump(os.path.join(self.folderpath,'mainstore'),
                        excluded_schemas=self.getExcluded(), options=options))

    def step_dumpaux(self):
        """Dump aux db"""
        checkedDbstores = self.batch_parameters.get('checkedDbstores')
        checkedDbstores = checkedDbstores.split(',') if checkedDbstores else self.db.stores_handler.dbstores.keys()
        dbstoreconf = Bag()
        dbstorefolder = os.path.join(self.db.application.instanceFolder, 'dbstores')
        options = self.batch_parameters['options']
        for s in self.btc.thermo_wrapper(checkedDbstores,line_code='dbl',message=lambda item, k, m, **kwargs: 'Dumping %s' %item):
            with self.db.tempEnv(storename=s):
                self.filelist.append(self.db.dump(os.path.join(self.folderpath,s),
                                    dbname=self.db.stores_handler.dbstores[s]['database'],
                                    excluded_schemas=self.getExcluded(),
                                    options=options))
                dbstoreconf[s] = Bag(os.path.join(dbstorefolder,'%s.xml' %s))
        confpath = os.path.join(self.folderpath,'_dbstores.xml')
        dbstoreconf.toXml(confpath)
        self.filelist.append(confpath)

    def getExcluded(self):
        checked = self.batch_parameters['dumppackages'].split(',')
        result = []
        for k in self.db.packages.keys():
            if not k in checked:
                result.append(k)
        return result


    def step_end(self):
        oldrec = dict(self.dump_rec)
        self.dump_rec.update(end_ts=datetime.datetime.now())
        self.tblobj.update(self.dump_rec,old_record=oldrec)
        self.db.commit()
        if len(self.filelist)==1 and self.db.implementation=='postgres':
            filepath = self.filelist[0] #/.../pippo/mainstore.pgd --> /.../pippo.pgd
            destname = '%s.pdg' %self.dump_name
            destpath = self.page.site.getStaticPath(self.dumpfolder,'backups',destname)
            shutil.move(filepath, destpath)
            shutil.rmtree(self.folderpath)
            self.result_url = self.page.site.getStaticUrl(self.dumpfolder,'backups',destname)
            return
        self.zipPath='%s.zip' %self.folderpath
        self.page.site.zipFiles(file_list=self.filelist, zipPath=self.zipPath)
        shutil.rmtree(self.folderpath)
        self.result_url = self.page.site.getStaticUrl(self.dumpfolder,'backups','%s.zip' %self.dump_name)

    def result_handler(self):
        resultAttr = dict(url=self.result_url)
        return 'Dump complete', resultAttr

    def table_script_stores(self, tc, **kwargs):
        dbstores = self.db.dbstores
        if not dbstores:
            return
        def _dbstorestruct(struct):
            r=struct.view().rows()
            r.checkboxcolumn(checkedId='#dump_pars.checkedDbstores',checkedField='dbstore',name='C.')
            r.cell('dbstore',name='Db Store',width='30em')
        storespane = tc.contentPane(title='Stores',_workspace=True)
        self.mixinComponent('gnrcomponents/framegrid:FrameGrid')
        dbstorebag = Bag()
        for s in dbstores:
            dbstorebag.setItem(s,None,dbstore=s,_checked=False)
        fg = storespane.bagGrid(frameCode='dbstoregrid',struct=_dbstorestruct,
                        datapath='#WORKSPACE.dbstores',storepath='#WORKSPACE.store',datamode='attr')
        fg.data('#WORKSPACE._loadedstore',dbstorebag)
        fg.dataFormula('#WORKSPACE.store','loadedstore',loadedstore='=#WORKSPACE._loadedstore',_onBuilt=True)
        fg.top.bar.replaceSlots('#','*,searchOn,5')

    def table_script_packages(self, tc, **kwargs):
        pkgPane = tc.contentPane(title='Packages')
        fb = pkgPane.div(padding='10px').formbuilder(cols=1,border_spacing='3px',nodeId='dump_pars')
        fb.textbox(value='^.name',lbl='!!Backup name')
        values = []
        defaultchecked = []
        for k,v in self.db.packages.items():
            if not v.attributes.get('dump_exclude'):
                defaultchecked.append(k)
            values.append('%s:%s,/' %(k,v.attributes.get('name_long',k)))
        fb.data('.dumppackages',','.join(defaultchecked))
        fb = pkgPane.div(padding='10px').formbuilder(cols=1,border_spacing='3px')
        fb.checkBoxText(value='^.dumppackages',values=','.join(values))



    def table_script_options(self, tc, **kwargs):
        optionsPane = tc.contentPane(title='Options', datapath='.options')
        fb = optionsPane.div(padding='10px').formbuilder(cols=1,border_spacing='3px')
        fb.checkBox(value='^.data_only', label='Data Only')
        fb.checkBox(value='^.no_owner', label='No Owner')
        fb.checkBox(value='^.schema_only', label='Schema Only')
        fb.checkBox(value='^.no_privileges', label='No Privileges')
        fb.checkBox(value='^.quote_all_identifiers', label='Quote all identifiers')
        fb.checkBox(value='^.storeonly', label='Store only')

        fb.checkBox(value='^.plain_text', label='Plain text')
        fb.checkBox(value='^.clean', label='Clean', row_visible='^.plain_text')
        fb.checkBox(value='^.if_exists', label='If exists', row_visible='^.plain_text')
        fb.checkBox(value='^.create', label='Create', row_visible='^.plain_text')

    def table_script_parameters_pane(self, pane, **kwargs):
        tc = pane.tabContainer(height='500px',width='700px')
        self.table_script_packages(tc)
        self.table_script_stores(tc)
        self.table_script_options(tc)
