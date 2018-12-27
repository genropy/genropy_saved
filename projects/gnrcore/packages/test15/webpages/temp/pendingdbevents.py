# -*- coding: utf-8 -*-

# rpcurl.py
# Created by Francesco Porcari on 2011-11-12.
# Copyright (c) 2011 Softwell. All rights reserved.

"Test page description"
import datetime
from gnr.core.gnrdecorator import public_method

class GnrCustomWebPage(object):
    py_requires="gnrcomponents/testhandler:TestHandlerFull"

    def test_1_pendingDbEvents(self,pane):
        pane.button('No commit',fire='.no_commit')
        pane.button('do commit',fire='.do_commit')
        pane.dataRpc(None,self.testPendingDbevents,do_commit='^.do_commit',_fired='^.no_commit')
    

    def test_2_autoInsert(self,pane):
        pane.button('AutoInsert',fire='.autoInsert')
        pane.dataRpc(None,self.testAutoInsert,_fired='^.autoInsert')
    

    @public_method
    def testPendingDbevents(self,do_commit=None,**kwargs):
        self.db.table('adm.user').touchRecords(where='$id IS NOT NULL')
        if do_commit:
            self.db.commit()

    @public_method
    def testAutoInsert(self,**kwargs):
        with self.db.tempEnv(autoCommit=True):
            self.db.table('fatt.cliente_tipo').insert(dict(codice='ZZZ',descrizione="AAA"))