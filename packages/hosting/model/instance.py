#!/usr/bin/env python
# encoding: utf-8

from gnr.app.gnrdeploy import InstanceMaker, SiteMaker
from gnr.core.gnrbag import Bag
import os

class Table(object):

    def config_db(self, pkg):
        tbl =  pkg.table('instance', rowcaption='')
        self.sysFields(tbl)
        tbl.column('code',size=':10',name_long='!!Instance Code')
        tbl.column('description',name_long='!!Instance Description')
        tbl.column('repository_name', dtype='T', name_long='!!Repository Name') # Optional
        tbl.column('path',dtype='T',name_long='!!Instance Path')
        tbl.column('site_path',dtype='T',name_long='!!Site Path')
        tbl.column('hosted_data','X',name_long='!!Hosted data',_sendback=True)  
        tbl.column('client_id',size=':22',name_long='!!Client id').relation('client.id',mode='foreignkey')

    def create_instance(self, code):
        instanceconfig=Bag(self.pkg.instance_template())
        instanceconfig.setAttr('db',dbname=code)
        base_path=os.path.dirname(self.pkg.instance_folder(code))
        im=InstanceMaker(code, base_path=base_path, config=instanceconfig)
        im.do()
        return im.instance_path
        
    def create_site(self, code):
        siteconfig=Bag(self.pkg.site_template())
        base_path=os.path.dirname(self.pkg.site_folder(code))
        sm=SiteMaker(code, base_path=base_path, config=siteconfig)
        sm.do()
        return sm.site_path

    def trigger_onInserting(self, record_data):
        self.create_instance(record_data['code'])
        self.create_site(record_data['code'])
        self.pkg.db_setup(record_data['code'])
        for pkg in self.db.application.packages.values():
            if hasattr(pkg,'onInstanceCreated'):
                getattr(pkg,'onInstanceCreated')(record_data)
    
    def trigger_onUpdating(self, record_data, old_record):
        for pkg in self.db.application.packages.values():
            if hasattr(pkg,'onInstanceUpdated'):
                getattr(pkg,'onInstanceUpdated')(record_data)
                