# encoding: utf-8
from __future__ import print_function
from builtins import str
from builtins import object
import os 
from gnr.core.gnrlang import gnrImport

class Table(object):
    def config_db(self,pkg):
        tbl=pkg.table('upgrade', pkey='codekey',pkey_columns='pkg,filename', pkey_columns_joiner='|',
                        name_long='!!Upgrade ', name_plural='!!Upgrades',caption_field='codekey')
        self.sysFields(tbl,id=False)
        tbl.column('codekey',size=':80',name_long='Identifier')
        tbl.column('pkg',size=':20',name_long='Package')
        tbl.column('filename', size=':40', name_long='!!Filename')
        tbl.column('error', name_long='!!Upgrade error', name_short='!!Error')

    def upgradePath(self,codekey):
        pkg,filename = codekey.split('|')
        return os.path.join(self.db.application.packages[pkg].packageFolder,'lib','upgrades','%s.py' %filename)
        

    def runUpgrades(self):
        alreadyRun= self.query(where='$error IS NULL').fetchAsDict('codekey')
        for pkg,pkgobj in list(self.db.application.packages.items()):
            upgradefolder = os.path.join(pkgobj.packageFolder,'lib','upgrades') 
            if not os.path.isdir(upgradefolder):
                continue
            for f in sorted(os.listdir(upgradefolder)):
                filename,ext = os.path.splitext(f)
                if ext!='.py':
                    continue
                upgradekey = '%s|%s' %(pkg,filename)
                if upgradekey not in alreadyRun:
                    print('upgrade',upgradekey)
                    self.runUpgrade(upgradekey)
    
    def runUpgrade(self,codekey):
        pkg,filename = codekey.split('|')
        filepath = self.upgradePath(codekey)
        error = None
        try:
            m = gnrImport(filepath)
            error = m.main(self.db)
        except Exception as e:
            self.db.rollback()
            error = str(e)
        with self.recordToUpdate(codekey,insertMissing=True) as r:
            r['error'] = error
            r['pkg'] = pkg
            r['filename'] = filename
        if error:
            print('ERROR',codekey,error)
        self.db.commit()

    def use_dbstores(self,**kwargs):
        return True