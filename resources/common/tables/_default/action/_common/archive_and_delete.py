# -*- coding: utf-8 -*-

# test_special_action.py
# Created by Francesco Porcari on 2010-07-02.
# Copyright (c) 2011 Softwell. All rights reserved.

from gnr.web.batch.btcaction import BaseResourceAction
from gnr.core.gnrbag import Bag
from collections import defaultdict
import shutil
import gzip
import os

caption = 'Archive and delete'
tags = '_DEV_,superadmin'
description = 'Archive and delete'

class Main(BaseResourceAction):
    batch_prefix = 'aad'
    batch_title = 'Archive and delete'
    batch_cancellable = True
    batch_delay = 0.5
    batch_steps = 'get_dependencies,archive,delete_archived'

    def step_get_dependencies(self):
        "Get dependencies"
        self.curr_records = self.tblobj.query(where='$id IN :pkeys',pkeys=self.get_selection_pkeys(),addPkeyColumns=False,
                                    excludeLogicalDelete=False,excludeDraft=False).fetch()
        name = self.batch_parameters.get('name') or 'archive_for_%s' %self.tblobj.fullname.replace('.','_')
        self.source_folder = self.page.site.getStaticPath('site:export_archive','source',name)
        self.archive_path = self.page.site.getStaticPath('site:export_archive','source',name,'records',autocreate=True)
        self.files_to_copy = self.page.site.getStaticPath('site:export_archive','source',name,'files',autocreate=True)
        self.result_path = self.page.site.getStaticPath('site:export_archive','results','%s.zip' %name,autocreate=-1)
        self.result_url = self.page.site.getStaticUrl('site:archived_records','results','%s.zip' %name)
        self.tableDependencies = self.tblobj.dependenciesTree(self.curr_records)
        self.index_tables = list(self.db.tablesMasterIndex(hard=True)['_index_'].keys())
        self.mode = self.batch_parameters.get('mode')

    def step_archive(self):
        "Prepare Archive file"
        if self.mode == 'D':
            return
        archive = Bag()
        for t in self.index_tables:
            tablename = t.replace('/','.')
            if tablename==self.tblobj.fullname:
                archive[t] = self.curr_records
            else:
                d = self.tableDependencies.get(tablename)
                if d:
                    pkeys = d['one'].union(d['many'])
                    reltblobj = self.db.table(tablename)
                    archive[t] = reltblobj.query(where='$%s IN :pkeys' %reltblobj.pkey,
                                                pkeys=list(pkeys),
                                                addPkeyColumn=False,bagFields=True,
                                                excludeDraft=False,excludeLogicalDeleted=False).fetch()
            archivingTable = self.db.table(tablename)         
            if hasattr(archivingTable,'onArchiveExport') and (t in archive):
                files = defaultdict(list)
                filelist = []
                reltblobj.onArchiveExport(archive[t],files=files)
                for pkey,pathlist in list(files.items()):
                    destfolder = os.path.join(self.files_to_copy,tablename,pkey)
                    if not os.path.exists(destfolder):
                        os.makedirs(destfolder)
                    for sn in pathlist:
                        if not sn.exists:
                            continue
                        basename = sn.basename
                        destpath = os.path.join(destfolder,basename)
                        sn.copy(destpath)
                        #shutil.copy(sn,destpath)        
        archive.makePicklable()
        archive.pickle('%s.pik' %self.archive_path)
        self.page.site.zipFiles(self.source_folder,self.result_path)

       #zipPath = '%s.gz' %self.archive_path
       #with open('%s.pik' %self.archive_path,'rb') as sfile:
       #    with gzip.open(zipPath, 'wb') as f_out:
       #        f_out.writelines(sfile)
        #os.remove('%s.pik' %self.archive_path)



    def step_delete_archived(self):
        "Delete archived"
        if self.mode == 'A':
            return
        for t in reversed(self.index_tables):
            t = t.replace('/','.')
            if t in self.tableDependencies:
                s = self.tableDependencies.get(t)['many']
                if s:
                    self.db.table(t).sql_deleteSelection(_pkeys=list(s))
        self.tblobj.sql_deleteSelection(_pkeys=[r[self.tblobj.pkey] for r in self.curr_records])
        self.db.commit()

    def result_handler(self):
        if self.mode == 'D':
            return 'Completed', None
        resultAttr = dict(url=self.result_url)
        return 'Archived %s' %self.tblobj.name_plural, resultAttr
    
    
    def table_script_parameters_pane(self, pane, table=None,**kwargs):
        fb = pane.div(padding='10px').formbuilder(cols=1,border_spacing='3px')
        fb.filteringSelect(value='^.mode', lbl='Mode', values='D:Delete only,A:Archive only,AD:Archive and delete',validate_notnull=True)
        fb.textbox(value='^.name', lbl='Filename', disabled="^.mode?=(#v=='D' || #v==null)")
        # fb.checkbox(value='^.delete_archived',label='Delete archived')

