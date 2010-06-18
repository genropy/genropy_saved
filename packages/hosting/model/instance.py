#!/usr/bin/env python
# encoding: utf-8

from gnr.app.gnrdeploy import InstanceMaker, SiteMaker
import os.path
from gnr.core.gnrbag import Bag

class Table(object):

    def config_db(self, pkg):
        tbl =  pkg.table('instance', rowcaption='')
        self.sysFields(tbl)
        tbl.column('code',size=':10',name_long='!!Instance Code')
        tbl.column('description',name_long='!!Instance Description')
        tbl.column('repository_name', dtype='T', name_long='!!Repository Name') # Optional
        tbl.column('path',dtype='T',name_long='!!Instance Path')
        tbl.column('site_path',dtype='T',name_long='!!Site Path')
        tbl.column('hosted_data','X',name_long='!!Hosted data')  
        tbl.column('client_id',size=':22',name_long='!!Client id').relation('client.id',mode='foreignkey')
        # dtype -> sql
        #   I       int
        #   R       float
        #   DH      datetime
        #   H       time
        # 
    def create_instance(self, name, path, instanceconfig):
        instanceconfig=Bag(instanceconfig)
        instanceconfig.pop('application')
        instanceconfig.pop('menu')
        instanceconfig.pop('packages.hosting')
        base_path=os.path.dirname(os.path.realpath(path))
        im=InstanceMaker(name, base_path=base_path, config=instanceconfig)
        im.do()
        return im.instance_path
        
    def create_site(self, name, path, siteconfig):
        siteconfig=Bag(siteconfig)
        siteconfig.pop('secret')
        siteconfig.pop('instances')
        base_path=os.path.dirname(os.path.realpath(path))
        sm=SiteMaker(name, base_path=base_path, config=siteconfig)
        sm.do()
        return sm.site_path

    def trigger_onInserting(self, record_data):
        pass