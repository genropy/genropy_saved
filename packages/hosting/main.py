
#!/usr/bin/env python
# encoding: utf-8
from gnr.app.gnrdbo import GnrDboTable, GnrDboPackage, Table_counter, Table_userobject
import os

class Package(GnrDboPackage):
    def config_attributes(self):
        return dict(comment='hosting package',sqlschema='hosting',
                name_short='Hosting', name_long='Hosting', name_full='Hosting')

    def config_db(self, pkg):
        pass

    def hosting_folder(self):
        return os.path.realpath(os.path.join(self.db.application.instanceFolder,self.attributes['hostingFolder']))

    def instance_folder(self,instance_name):
        return os.path.join(self.hosting_folder(),'instances',instance_name)
        
    def instance_exists(self,instance_name):
        """check if the isnstance exists"""
        return instance_name and os.path.isfile(os.path.join(self.instance_folder(instance_name),'instanceconfig.xml'))
        
    def site_folder(self,instance_name):
        return os.path.join(self.hosting_folder(),'sites',instance_name)

    def site_exists(self,instance_name):
        """check if the site exists"""
        return instance_name and os.path.isfile(os.path.join(self.site_folder(instance_name),'siteconfig.xml'))
                

class Table(GnrDboTable):
    pass
