# -*- coding: UTF-8 -*-

# dbselect_bug.py
# Created by Francesco Porcari on 2012-01-03.
# Copyright (c) 2012 Softwell. All rights reserved.

"Test page description"
from gnr.core.gnrdecorator import public_method
from gnr.core.gnrbag import Bag
from time import sleep

class GnrCustomWebPage(object):
    py_requires="gnrcomponents/testhandler:TestHandlerFull"
    dojo_source = True

    def windowTitle(self):
        return ''
         
    def test_0_firsttest(self,pane):
        """dbselect with auxcol"""
        fb = pane.formbuilder(cols=1, border_spacing='4px')
        fb.dbSelect(dbtable='adm.user',value='^.user_id',lbl='Sigla',selected_username='.username',auxColumns='username',width='25em')
        #fb.data('.username','...')
        #fb.div('^.user_id',lbl='User')
        fb.div('^.username',lbl='Username')
        
    def test_1_firsttest(self,pane):
        """dbselect no auxcol"""
        fb = pane.formbuilder(cols=1, border_spacing='4px')
        fb.dbSelect(dbtable='adm.user',value='^.user',lbl='Sigla',selected_username='.username',width='25em')
        fb.data('.username','...')
        fb.div('^.user',lbl='User')
        fb.div('^.username',lbl='Username')
        
    def test_2_firsttest(self,pane):
        fb = pane.formbuilder(cols=1, border_spacing='4px')
        fb.dbSelect(dbtable='glbl.provincia',value='^.sigla',lbl='Sigla',width='25em')
        fb.dataRecord('.provincia','glbl.provincia',pkey='^.sigla',applymethod='testhotutto')
    
    def test_3_condition(self,pane):
        fb = pane.formbuilder(cols=2, border_spacing='4px')
        fb.dbSelect(dbtable='glbl.regione',value='^.regione',lbl='Regione',width='25em',selected_nome='pippo')
        fb.div('^pippo')
        fb.dbSelect(dbtable='glbl.provincia',value='^.sigla',condition='$regione=:regione',condition_regione='^.regione',
                        lbl='Sigla',width='25em',xvalidate_notnull=True,xvalidate_notnull_error='Manca il valore')
    
    def rpc_testhotutto(self,record,**kwargs):
        print record['@localita']
        


    def test_4_dbselectrpc(self,pane):
        """getuser custom rpc"""
        fb = pane.formbuilder(cols=1, border_spacing='4px')
        fb.dbSelect(value='^.user',width='25em',lbl='User',auxColumns='status,auth_tags',
                        method=self.getUserCustomRpc)

    @public_method
    def getUserCustomRpc(self,_querystring=None,_id=None,**kwargs):
        result = Bag()
        if _id:
            f = self.db.table('adm.user').query(where='$id = :u',u=_id).fetch()
        else:
            sleep(2)
            f = self.db.table('adm.user').query(where='$username ILIKE :u',u='%s%%' %_querystring.replace('*','')).fetch()
        for i,r in enumerate(f):
            result.setItem('%s_%s' %(r['id'],i),None,caption='%s - %s' %(r['username'], r['auth_tags']),
                status=r['status'],auth_tags=r['auth_tags'],_pkey=r['id'],username=r['username'])
        return result,dict(columns='username,status,auth_tags',headers='Name,Status,Tags')




