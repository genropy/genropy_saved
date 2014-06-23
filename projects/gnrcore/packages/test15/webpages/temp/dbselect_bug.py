# -*- coding: UTF-8 -*-

# dbselect_bug.py
# Created by Francesco Porcari on 2012-01-03.
# Copyright (c) 2012 Softwell. All rights reserved.

"Test page description"
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
        