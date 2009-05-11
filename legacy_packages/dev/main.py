#!/usr/bin/env python
# encoding: utf-8


import sys
import os

class Package(object):
    def config_attributes(self):
        return dict(comment='dev package',
                name_short='dev', name_long='dev', name_full='dev')
        
    def config_db(self, pkg):
        #developer table
        t = pkg.table('developer', pkey='id')
        t.column('id', size='22')
        t.column('shortname', size='12')
        t.column('name', size='30', validate_case='capitalize')
        t.column('password', size='12', input_mode='hidden')
        t.column('tags')
        
        
        #customer table
        t = pkg.table('customer', pkey='id')
        t.column('id', size='22')
        t.column('shortname', size='12')
        t.column('name', size='50')
        t.column('password', size='12')
        t.column('tags')
        #package table
        t = pkg.table('package', pkey='id')
        t.column('id', size='6')
        t.column('description', size='40')
        t.column('customer_id', size='22').relation('dev.customer.id')
        
        #role table
        t = pkg.table('role', pkey='code')
        t.column('code', size='10')
        t.column('description', size='30')
        
        #package-developer table
        t = pkg.table('package_developer')
        t.column('id', size='22', pkey='id')
        t.column('package_id', size='6').relation('dev.package.id')
        t.column('developer_id', size='22').relation('dev.developer.id')
        t.column('role', size='10').relation('dev.role.code')
        
        
        
