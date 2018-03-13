#!/usr/bin/env python
# encoding: utf-8
from gnr.app.gnrdbo import GnrDboTable, GnrDboPackage

class Package(GnrDboPackage):
    def config_attributes(self):
        return dict(comment='email package',sqlschema='email',
                name_short='Email', name_long='Email', name_full='Email')
                
    def config_db(self, pkg):
        pass
        
    def loginUrl(self):
        return 'email/login'

    def services(self):
        return [dict(service_name='mail',resource='emailservice')]
        
class Table(GnrDboTable):
    pass
