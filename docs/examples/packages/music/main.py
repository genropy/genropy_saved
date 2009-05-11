#!/usr/bin/env python
# encoding: utf-8

class Package(object):
    def config_attributes(self):
        return dict(comment='My music package',
                name_short='Music', name_long='Music package', name_full='Music package')
        
    def config_db(self, pkg):
        pass
