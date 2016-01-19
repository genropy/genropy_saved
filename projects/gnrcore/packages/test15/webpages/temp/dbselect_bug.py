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
         

    def test_5_combobug(self,pane):
        fb = pane.formbuilder(cols=1, border_spacing='4px')
        fb.dbCombobox(dbtable='adm.user',value='^.user',lbl='dbCombo',
                    width='25em',hasDownArrow=True)
        fb.combobox(value='^.combobox',values='Pippo,Pluto,Paperino',lbl='Combo')

        fb.filteringSelect(value='^.filtering',values='pippo:Pippo,pluto:Pluto,paperino:Paperino',lbl='Filtering')


    def test_0_firsttest(self,pane):
        """dbselect with auxcol"""
        fb = pane.formbuilder(cols=1, border_spacing='4px')
        fb.dbSelect(dbtable='adm.user',value='^.user_id',lbl='User',

                    selected_username='.username',width='25em',
                    hasDownArrow=True)

        fb.dbCombobox(dbtable='adm.user',value='^.username',lbl='Combo',
                    selected_username='.username',width='25em',
                    hasDownArrow=True)

        fb.dbSelect(dbtable='adm.user',value='^.user_id_2',lbl='zzz',
                    auxColumns='$username',width='25em',
                    hasDownArrow=True)
        #fb.data('.username','...')
        #fb.div('^.user_id',lbl='User')
        #fb.dataController("genro.bp(true);",user_id='^.user_id')
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
        

    def test_6_clientmethod(self,pane):
        fb = pane.formbuilder(cols=1, border_spacing='4px')
        fb.callbackSelect(value='^.test',callback="""function(kw){
                console.log('pars',kw,this)
                var _id = kw._id;
                var _querystring = kw._querystring;
                var data = [{name:'Mario Rossi',addr:'Via del Pero',state:'Milano',_pkey:'mrossi',caption:'Mario Rossi (mrossi)'},
                              {name:'Luigi Bianchi',addr:'Via del Mare',state:'Roma',_pkey:'lbianchi',caption:'Luigi Bianchi (lbianchi)'},
                              {name:'Carlo Manzoni',addr:'Via Bisceglie',state:'Firenze',_pkey:'cmanzoni',caption:'Carlo Manzoni (cmanz)'},
                              {name:'Marco Vanbasten',addr:'Via orelli',state:'Como',_pkey:'mvan',caption:'Marco Vanbasten(mvan)'},
                              {name:'',caption:'',_pkey:null}
                              ]
                var cbfilter = function(n){return true};
                if(_querystring){
                    _querystring = _querystring.slice(0,-1).toLowerCase();
                    cbfilter = function(n){return n.name.toLowerCase().indexOf(_querystring)>=0;};
                }else if(_id){
                    cbfilter = function(n){return n._pkey==_id;}
                }
                data = data.filter(cbfilter);
                return {headers:'name:Customer,addr:Address,state:State',data:data}
            }""",auxColumns='addr,state',lbl='Callback select',hasDownArrow=True,nodeId='cbsel')


    def test_4_dbselectrpc(self,pane):
        """getuser custom rpc"""
        fb = pane.formbuilder(cols=1, border_spacing='4px')
        fb.remoteSelect(value='^.user',width='25em',lbl='User',auxColumns='status,auth_tags',
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




