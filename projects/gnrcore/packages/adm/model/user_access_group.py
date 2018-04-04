#!/usr/bin/env python
# encoding: utf-8

class Table(object):
    def config_db(self, pkg):
        tbl = pkg.table('user_access_group', pkey='id', name_long='!!User access', name_plural='!!User access')
        self.sysFields(tbl)
        tbl.column('user_id',size='22' ,group='_',name_long='!!User').relation('user.id',relation_name='access_groups',
                                                                                mode='foreignkey',onDelete='cascade')
        tbl.column('access_group_code',size=':10' ,group='_',name_long='!!Access group').relation('access_group.code',
                                                                                                    relation_name='access_users',
                                                                                                    mode='foreignkey',onDelete='cascade')   

    def allowedUser(self,user_id=None):
        access_groups = self.query(where='$user_id=:uid',uid=user_id,
                                    columns='@access_group_code.allowed_ip AS allowed_ip').fetch()
        allowed_ip = set([])
        for ag in access_groups:
            allowed_ip = allowed_ip.union(set(ag['allowed_ip'].split(',') if ag['allowed_ip'] else []))   
        return self.validateIp(','.join(allowed_ip)) if allowed_ip else None
                              
    def validateIp(self,allowed_ip):
        currentPage = self.db.application.site.currentPage
        iplist = currentPage.connection.ip.split('.')
        for ip in allowed_ip.split(','):
            ipcheck = ip.split('.') 
            if iplist[0:len(ipcheck)] == ipcheck:
                return True
        return False