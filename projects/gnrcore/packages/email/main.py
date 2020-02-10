#!/usr/bin/env python
# encoding: utf-8
from gnr.core.gnrstring import boolean
from gnr.app.gnrdbo import GnrDboTable, GnrDboPackage

class Package(GnrDboPackage):
    def config_attributes(self):
        return dict(comment='email package',sqlschema='email',
                name_short='Email', name_long='Email', name_full='Email')
                
    def config_db(self, pkg):
        pass
    
    def required_packages(self):
        return ['gnrcore:adm']
        
    def loginUrl(self):
        return 'email/login'

    def services(self):
        return [dict(service_name='mail',resource='emailservice')]
        
class Table(GnrDboTable):
    def use_dbstores(self,forced_dbstore=None, env_forced_dbstore=None,**kwargs):
        result = forced_dbstore or \
                env_forced_dbstore or \
                boolean(self.pkg.attributes.get('use_dbstores','f'))
        return result

