#!/usr/bin/env python
# encoding: utf-8

class Package(object):
    def config_attributes(self):
        return dict(comment='ticketapp package',
                name_short='ticketapp', name_long='ticketapp', name_full='ticketapp')
        
    def config_db(self, pkg):
        testtbl = pkg.table('test', pkey='id')
        testtbl.column('id', size='22')
