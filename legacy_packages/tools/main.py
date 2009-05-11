#!/usr/bin/env python
# encoding: utf-8

class Package(object):
    def config_attributes(self):
        return dict(comment='tools package',
                name_short='tools', name_long='tools', name_full='tools')
        
    def config_db(self, pkg):
        pass


class Table(object):
    pass

