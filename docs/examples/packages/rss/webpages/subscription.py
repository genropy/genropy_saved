#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
""" GnrDojo Hello World """

import datetime
from gnr.core.gnrbag import Bag, DirectoryResolver

#-------  configure: customize this configuration ------
class GnrCustomWebPage(object):
    def main(self, root, **kwargs):
        window = self.rootLayoutContainer(root, padding='2px')
        layout = window.layoutContainer('maincontainer', height='100%')
        layout.contentPane(layoutAlign='top', _class='titlepane').span('Subscribe Page')
        
        client = layout.contentPane(layoutAlign='client')
        formcont = client.div(_class='clientform')
        tbl = formcont.table(_class='table')
        row1 = tbl.tr(_class='row')
        row1.td('Username', _class='label' )
        row1.input(_class='field',datasource='user.username', validate_len='3,10', validate_notNull='Y', validate_server='isUserOk')
        
        row2 = tbl.tr(_class='row')
        row2.td('Password', _class='label')
        row2.input(_class='field', type='password', datasource='user.password', validate_len='3,10', validate_notNull='Y')
        
        row3 = tbl.tr(_class='row')
        row3.td('Confirm password', _class='label')
        row3.input(_class='field', type='password', datasource='confirm.password',
                    validate_len='3,10', validate_notNull='Y', validate_ext="""
                        function(kw){
                            if (kw.value==genro.getData('user.password')){
                                return kw.value
                            } else {
                                throw {'code':'password_mismatch'}
                            }
                        }
                        """)
        
        
        row4 = tbl.tr(_class='row')
        row4.td('email', _class='label')
        row4.input(_class='field', datasource = 'user.email', validate_notNull='Y')
        save_btn = row4.td().button(caption='submit', gnrId='savebtn')
        
        save_btn.func('saverecord','',  """
                      var params = {'dbtable': 'rss.user'};
                      params['recordBag'] = genro.getData('user');                      
                      var result = genro.rpc.remoteCall('app.saveRecord', params, null, 'POST');
                      genro.dlg.message(result,'',10000);
                      """)
                      
        save_btn.subscribe(save_btn, event='onClick', func='*saverecord')
        
    def authenticateUser(self, user, password):
        dbtable = 'rss.user'
        record = self.app.db.table(dbtable).record(pkey=user).output('bag') 
        if(record):
            return (record['password'] == password)
        return False
        
    def rpc_isUserOk(self, node, value, oldvalue, pars):
        r = self.app.db.table('rss.user').record(value)
        if r:
            raise GnrWebClientError('invalid_username')
        return value

