#!/usr/bin/env python
# encoding: utf-8
import os

from gnr.core.gnrbag import Bag

from gnr.core.gnrstring import templateReplace, splitAndStrip

class Package(object):
    def config_attributes(self):
        return dict(comment='MNT package',
                    sqlprefix='',
                    name_short='MNT',
                    name_long='MNT',
                    name_full='MNT',
                    noTestForMerge=True)


    def authenticate(self, username):
        result = self.application.db.query('mnt.jos_users', columns='*',
                                           where='$username = :user', user=username).fetch()
        if result:
            result = dict(result[0])
            result['tags'] = 'admin,_DEV_'
            result['pwd'] = result.pop('password')
            #result['userid'] = result['id']
            #result['id'] = username            
            return result
            
            
    def onAuthentication(self, avatar): 
        pass

    def loginUrl(self):
        return 'mnt/login.py'