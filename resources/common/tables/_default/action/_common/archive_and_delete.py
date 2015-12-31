# -*- coding: UTF-8 -*-

# test_special_action.py
# Created by Francesco Porcari on 2010-07-02.
# Copyright (c) 2011 Softwell. All rights reserved.

from gnr.web.batch.btcaction import BaseResourceAction
from gnr.core.gnrbag import Bag
import gzip
import os

caption = 'Archive and delete'
tags = '_DEV_,superadmin'
description = 'Archive and delete'

class Main(BaseResourceAction):
    batch_prefix = 'aad'
    batch_title = 'Archive and delete'
    batch_cancellable = False
    batch_delay = 0.5
    batch_immediate = True
    batch_steps = 'get_dependencies,archive,delete_archived'

    def step_get_dependencies(self):
        "Get dependencies"
        self.curr_records = self.tblobj.query(where='$id IN :pkeys',pkeys=self.get_selection_pkeys(),addPkeyColumns=False,
                                    excludeLogicalDelete=False,excludeDraft=False).fetch()
        name = self.batch_parameters.get('name') or 'archive_for_%s' %self.tblobj.fullname.replace('.','_')
        self.archive_path = self.page.site.getStaticPath('site:archived_records',name,autocreate=True)
        self.archive_url = self.page.site.getStaticUrl('site:archived_records',name)
        self.tableDependencies = self.tblobj.dependenciesTree(self.curr_records)
        self.index_tables = self.db.tablesMasterIndex(hard=True)['_index_'].keys()

    def step_archive(self):
        "Prepare Archive file"
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
        archive.makePicklable()
        archive.pickle('%s.pik' %self.archive_path)
       #zipPath = '%s.gz' %self.archive_path
       #with open('%s.pik' %self.archive_path,'rb') as sfile:
       #    with gzip.open(zipPath, 'wb') as f_out:
       #        f_out.writelines(sfile)
        #os.remove('%s.pik' %self.archive_path)



    def step_delete_archived(self):
        "Delete archived"
        if not self.batch_parameters.get('delete_archived'):
            return
        for t in reversed(self.index_tables):
            t = t.replace('/','.')
            s = self.tableDependencies.get(t)['many']
            if s:
                self.db.table(t).sql_deleteSelection(_pkeys=list(s))
        self.tblobj.sql_deleteSelection(_pkeys=[r[self.tblobj.pkey] for r in self.curr_records])
        self.db.commit()

    def result_handler(self):
        resultAttr = dict(url='%s.pik' %self.archive_url)
        return 'Archived %s' %self.tblobj.name_plural, resultAttr

    def table_script_parameters_pane(self, pane, table=None,**kwargs):
        fb = pane.div(padding='10px').formbuilder(cols=1,border_spacing='3px')
        fb.textbox(value='^.name',lbl='Name')
        fb.checkbox(value='^.delete_archived',label='Delete archived')

