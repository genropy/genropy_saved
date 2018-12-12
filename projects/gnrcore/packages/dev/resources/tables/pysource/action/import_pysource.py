# -*- coding: utf-8 -*-

from gnr.web.batch.btcaction import BaseResourceAction
from gnr.core.gnrbag import Bag
import os
import sys
import shutil

caption = 'Import pysource'
tags = 'superadmin,_DEV_'
description=caption


class Main(BaseResourceAction):
    def do(self):
        sourcepath = self.batch_parameters['sourcepath']
        if sourcepath in sys.modules:
            m =  sys.modules[sourcepath]
            fname = os.path.splitext(m.__file__)[0]
            if os.path.basename(fname)=='__init__':
                dirpackage = os.path.dirname(fname)
                self.importDir(dirpackage)
            else:
                self.writeModule(fname)
        elif os.path.exists(sourcepath):
            if os.path.isdir(sourcepath):
                self.importDir(sourcepath)
            elif os.path.splitext(sourcepath)[1]=='.py':
                self.importModule(sourcepath)
        self.db.commit()

    def importModule(self,path):
        pass

    def importDir(self,sourcepath,parent_id=None):
        l = os.listdir(sourcepath)
        if '__init__.py' in l:
            rec = self.writeRecord(sourcepath,rtype='P',parent_id=parent_id)
            parent_id = rec['id']
        for r in l:
            fullpath = os.path.join(sourcepath,r)
            if fullpath.endswith('.py'):
                self.writeRecord(fullpath,rtype='M',parent_id=parent_id)
            elif os.path.isdir(fullpath):
                self.importDir(fullpath,parent_id=parent_id)
   
    def writeRecord(self,dirpackage,rtype=None,parent_id=None):
        name = os.path.basename(dirpackage)
        name = os.path.splitext(name)[0]
        where = ['$parent_id=:pid' if parent_id else '$parent_id IS NULL']
        where.append('$name=:n AND rtype=:rt')
        f = self.tblobj.query(where=' AND '.join(where),
                            pid=parent_id,rt=rtype,
                            n=name).fetch()
        if f:
            return f[0]

        rec = dict(name=name,rtype=rtype,parent_id=parent_id)
        self.tblobj.insert(rec)
        return rec


    def table_script_parameters_pane(self,pane,extra_parameters=None,record_count=None,**kwargs):
        fb = pane.formbuilder(cols=1,border_spacing='3px')
        fb.textbox(value='^.sourcepath',lbl='Path',width='30em')