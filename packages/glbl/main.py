#!/usr/bin/env python
# encoding: utf-8

class Package(object):
    def config_attributes(self):
        return dict(sqlschema='glbl',
                    comment='glbl package',
                    name_short='glbl',
                    name_long='glbl',
                    name_full='glbl')

    def config_db(self, pkg):
        pass



class Table(object):
    pass




