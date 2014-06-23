# -*- coding: UTF-8 -*-

# serverpath.py
# Created by Francesco Porcari on 2010-09-03.
# Copyright (c) 2010 Softwell. All rights reserved.

"""Serverpath"""
from gnr.core.gnrbag import Bag
class GnrCustomWebPage(object):
    py_requires = "gnrcomponents/testhandler:TestHandlerFull"
    auto_polling = 10
    user_polling = 3

    def test_0_serverpath(self, pane):
        fb = pane.formbuilder(cols=1, border_spacing='3px', datapath='test0')
        fb.data('.willbesetonserver', '', _serverpath='mytest0.mirror')
        fb.datetextbox(value='^.willbesetonserver', lbl='Set on server')
        #fb.button('Get Value from server', fire='.get')
        #fb.dataRpc('dummy', 'get_value_on_server', _fired='^.get', _onResult='alert(result)')

    def rpc_get_value_on_server(self):
        store = self.pageStore()
        return store.getItem('mytest0.mirror')


    def test_1_serverpath(self, pane):
        fb = pane.formbuilder(cols=1, border_spacing='3px', datapath='test1')
        fb.data('.mysync', '', _serverpath='mytest1.mirror')
        fb.textbox(value='^.mydata', lbl='Data')
        fb.div('^.mysync', lbl='Answer')
        fb.dataRpc('dummy', 'setval', value='^.mydata',
                   serverpath='mytest1.mirror')

    def test_2_serverpath(self, pane):
        fb = pane.formbuilder(cols=1, border_spacing='3px', datapath='test2')
        fb.data('.mysync', '', _serverpath='mytest2.mirror.ppp')
        fb.textbox(value='^.mydata', lbl='Data')
        fb.div('^.mysync', lbl='Answer')
        fb.dataRpc('dummy', 'setval', value='^.mydata',
                   serverpath='mytest2.mirror.ppp')

    def test_3_serverpath(self, pane):
        fb = pane.formbuilder(cols=1, border_spacing='3px', datapath='test3')
        fb.data('.mysync', '', _serverpath='mytest3.mirror')
        fb.textbox(value='^.mydata', lbl='Data')
        fb.div('^.mysync.answer.1.2.3', lbl='Answer')
        fb.dataRpc('dummy', 'setval', value='^.mydata',
                   serverpath='mytest3.mirror.answer.1.2.3')
        
    def test_4_innerpath(self,pane):
        pane.data('.mypath4.pino',None,serverpath='pierone')
        
        fb = pane.formbuilder(cols=2)
        fb.textbox(value='^.mypath4.pippero',lbl='pippero',attr_dbenv=True)
        fb.div('^.mypath4.elio',lbl='elio')
        fb.textbox(value='^.tosend',lbl='Value to send')
        fb.button('Send')
        fb.dataRpc('dummy','setval',serverpath='pierone.elio',value='^.tosend')
        #
    def test_5_serverpath_widget(self, pane):
        fb = pane.formbuilder(cols=1, border_spacing='3px')
        fb.textbox(value='^.mario',attr_serverpath='mario_path',lbl='con serverpath')

    def test_6_serverpath_dbenv(self, pane):
        fb = pane.formbuilder(cols=1, border_spacing='3px')
        fb.dbSelect(dbtable='polimed.specialita',value='^.specialita_id',
                    attr_dbenv='curr_spec',
                    attr_serverpath='specialita_bella',
                    lbl='!!Specialità')
        fb.dbSelect(dbtable='polimed.medico',value='^.medico_id',condition='@medico_specialita.specialita_id=:env_curr_spec')
        
             
    def rpc_setval(self, serverpath=None, value=None):
        with self.pageStore() as store:
            print 'setting at %s value %s' % (serverpath, value)
            store.setItem(serverpath, value)
        