#!/usr/bin/env python
# encoding: utf-8

from gnr.app.gnrdbo import GnrDboTable, GnrDboPackage, Table_counter, Table_userobject
import hashlib
from datetime import datetime
class Package(GnrDboPackage):
    
    def config_attributes(self):
        return dict(sqlschema='adm',
                    comment='Admin',
                    name_short='Adm',
                    name_long='!!Administration',
                    name_full='!!Administration Tool')
    
    def config_db(self, pkg):
        pass
    
    def authenticate(self, username):
        result = self.application.db.query('adm.user', columns='*',
                                           where='$username = :user AND $status != :waiting', 
                                           user=username, waiting='wait').fetch()
        if result:
            result = dict(result[0])
            result['tags'] = result.pop('auth_tags')
            result['pwd'] = result.pop('md5pwd')
            result['userid'] = result['id']
            result['id'] = username
            result['md5len']=len(result['pwd'])
            return result
            
    def onAuthentication(self, avatar):
        update_md5 = self.attributes.get('update_md5',False) not in ('N','n','F','f','False','false','FALSE','No','NO','no',False)
        if update_md5 and hasattr(avatar,'md5len') and avatar.md5len==32: 
            self.update_md5(avatar)
        avatar.login_pwd = None
        
    def onAuthenticated(self,avatar):
        if hasattr(avatar,'page'):
            self.connectionLog(avatar.page,'open',avatar)

    def connectionLog(self,page,event,avatar=None):
        connection = page.connection
        tblconnection = page.db.table('adm.connection')
        if event == 'open':
            userid = None
            if avatar.userid != avatar.id:
                userid = avatar.id
            new_connection_record = dict(id=connection.connection_id,username=avatar.id,
                                        userid=userid,start_ts=datetime.now(),
                                        ip=page.request.remote_addr,
                                         user_agent=page.request.get_header('User-Agent'))
            tblconnection.insertOrUpdate(new_connection_record)
        else:
            tblconnection.closeConnection(connection.connection_id,end_reason='logout')
        page.db.commit()
            
    def pageLog(self,page,event):
        tblservedpage = page.db.table('adm.served_page')
        if event == 'open':
            subscribed_tables=page.pageOptions.get('subscribed_tables',None)
            if subscribed_tables:
                for table in subscribed_tables.split(','):
                    assert page.db.table(table).attributes.get('broadcast')
            record_served_page = dict(page_id=page.page_id,end_reason=None,end_ts=None,
                                      connection_id=page.connection.connection_id,
                                      start_ts=datetime.now(),pagename=page.basename,
                                      subscribed_tables=subscribed_tables)
                                      
            tblservedpage.insertOrUpdate(record_served_page)
        else:
            tblservedpage.closePage(page_id=page.page_id,end_ts=datetime.now(),end_reason='unload')
        page.db.commit()
        
    def update_md5(self,avatar):
        md5_userid=hashlib.md5(str(avatar.userid)).hexdigest()
        new_pass=hashlib.md5(avatar.login_pwd+md5_userid).hexdigest()+':'+md5_userid
        self.application.db.table('adm.user').update(dict(id=avatar.userid,md5pwd=new_pass))
        self.application.db.commit()
        
    def newUserUrl(self):
        return 'adm/new_user'
    
    def modifyUserUrl(self):
        return 'adm/modify_user'
    
    def loginUrl(self):
        return 'adm/login'
        
    def onApplicationInited(self):
        pass
        
    def onSiteInited(self):
        db=self.application.db
        db.table('adm.connection').closePendingConnections(end_ts=datetime.now(), end_reason='sys_restart')
        db.commit()
        db.closeConnection()
    
class Table(GnrDboTable):
    pass
