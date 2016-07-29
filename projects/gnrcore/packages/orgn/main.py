#!/usr/bin/env python
# encoding: utf-8
from gnr.app.gnrdbo import GnrDboTable, GnrDboPackage

class Package(GnrDboPackage):
    def config_attributes(self):
        return dict(comment='Organizer package',sqlschema='orgn',sqlprefix=True,
                    name_short='Organizer', name_long='Organizer', name_full='Organizer package')
                    
    def config_db(self, pkg):
        pass
        
    def sidebarPlugins(self):
        if self.getPreference('organizer_enabled'):
            return 'organizer','frameplugin_organizer'

class Table(GnrDboTable):
    pass
