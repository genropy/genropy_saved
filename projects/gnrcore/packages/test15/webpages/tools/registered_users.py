# -*- coding: utf-8 -*-
# 
from __future__ import print_function
from builtins import object
from time import sleep
from gnr.core.gnrdecorator import public_method
"""Registered users tester"""
class GnrCustomWebPage(object):
    py_requires = "gnrcomponents/testhandler:TestHandlerFull"
    dojo_theme = 'tundra'
    dojo_version = '11'

    def test_1_user_lock(self, pane):
        fb = pane.formbuilder(cols=1,border_spacing='3px')
        fb.dbSelect(dbtable='adm.user',value='^.user_id',lbl='User',
                    selected_username='.username',width='25em',
                    hasDownArrow=True)
        fb.numberTextbox(value='^.seconds',lbl='Seconds')
        fb.checkbox(value='^.doError',label='Do Error')
        fb.button('Lock',fire='.lockUser')
        fb.div('^.result',lbl='Result')
        fb.dataRpc('.result',self.lockUser,username='=.username',seconds='=.seconds',
                    doError='=.doError',
                    _fired='^.lockUser')


    @public_method
    def lockUser(self,username=None,seconds=None,doError=None):
        seconds = seconds or 1
        with self.userStore(username) as store:
            if store is None:
                return 'Locked'
            elif doError:
                print(x)
            elif seconds:
                sleep(seconds)
                return 'done %s %s' %(self.getUuid(),seconds)
 