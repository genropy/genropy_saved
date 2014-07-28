#!/usr/bin/env python
# encoding: utf-8
from gnr.app.gnrdbo import GnrDboTable, GnrDboPackage, Table_counter
from gnr.app.gnrapp import GnrApp
import os

class Package(GnrDboPackage):
    def config_attributes(self):
        return dict(comment='hosting package', sqlschema='hosting',
                    name_short='Hosting', name_long='Hosting', name_full='Hosting')

    def config_db(self, pkg):
        pass

    def hosting_folder(self):
        return os.path.realpath(os.path.join(self.db.application.instanceFolder, self.attributes['hostingFolder']))

    def instance_template(self):
        """return """
        return os.path.join(self.hosting_folder(), 'instances', '_template', 'instanceconfig.xml')

    def site_template(self):
        """return """
        return os.path.join(self.hosting_folder(), 'sites', '_template', 'siteconfig.xml')


    def instance_folder(self, instance_name):
        return os.path.join(self.hosting_folder(), 'instances', instance_name)

    def instance_exists(self, instance_name):
        """check if the isnstance exists"""
        return instance_name and os.path.isfile(os.path.join(self.instance_folder(instance_name), 'instanceconfig.xml'))

    def site_folder(self, instance_name):
        return os.path.join(self.hosting_folder(), 'sites', instance_name)

    def site_exists(self, instance_name):
        """check if the site exists"""
        return instance_name and os.path.isfile(os.path.join(self.site_folder(instance_name), 'siteconfig.xml'))

    def db_synced(self, instance_name, storename=None, verbose=False):
        if self.instance_exists(instance_name):
            changes_dict = dict()
            app = GnrApp(os.path.join(self.instance_folder(instance_name), 'instanceconfig.xml'))
            if storename == '*':
                stores = [None] + app.db.dbstores.keys()
            else:
                stores = [storename]
            for storename in stores:
                app.db.use_store(storename)
                changes = app.db.model.check()
                if not verbose and changes:
                    return False
                else:
                    changes_dict[storename or 'Main'] = changes
            if not verbose:
                return True
            else:
                return changes
        else:
            raise Exception('Instance %s does not exists' % instance_name)

    def db_setup(self, instance_name, storename=None):
        if self.instance_exists(instance_name):
            app = GnrApp(self.instance_folder(instance_name))
            if storename == '*':
                stores = [None] + app.db.dbstores.keys()
            else:
                stores = [storename]
            for storename in stores:
                app.db.use_store(storename)
                changes = app.db.model.check()
                if changes:
                    app.db.model.applyModelChanges()
        else:
            raise Exception('Instance %s does not exists' % instance_name)

            for storename in stores:
                app.db.use_store(storename)

    def adaptHostedTable(self,table):
        pass

class Table(GnrDboTable):
    pass
