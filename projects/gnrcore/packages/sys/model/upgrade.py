# encoding: utf-8
import os 

class Table(object):
    def config_db(self,pkg):
        tbl=pkg.table('upgrade', pkey='codekey',pkey_columns='pkg,filename', pkey_columns_joiner='|',
                        name_long='!!Upgrade ', name_plural='!!Upgrades',caption_field='codekey')
        self.sysFields(tbl,id=False)
        tbl.column('codekey',name_long='Identifier')
        tbl.column('pkg',size=':20',name_long='Package')
        tbl.column('filename', size=':40', name_long='!!Filename')
        tbl.column('error', name_long='!!Upgrade error', name_short='!!Error')

    def upgradePath(self,codekey):
        pkg,filename = codekey.split('|')
        upgrade_file = self.application.site.getStaticPath('pkg:%s' %pkg,'lib','upgrades','%s.py' %filename)

    def runUpgrades(self):
        alreadyRun= self.query(where='$error IS NULL').fetchAsDict('codekey')
        for pkg in self.db.application.packages.keys():
            upgradefolder = self.application.site.getStaticPath('pkg:%s' %pkg,'lib','upgrades')
            if not os.path.isdir(upgradefolder):
                continue
            for filename in os.listdir(upgradefolder):
                upgradekey = '%s|%s' %(pkg,filename)
                if upgradekey in alreadyRun:
                    continue
                with self.recordToUpdate(upgradekey,insertMissing=True) as upgraderecord:
                    pass