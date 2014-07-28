# -*- coding: UTF-8 -*-
#--------------------------------------------------------------------------
# Copyright (c) : 2004 - 2007 Softwell sas - Milano 
# Written by    : Giovanni Porcari, Michele Bertoldi
#                 Saverio Porcari, Francesco Porcari , Francesco Cavazzana
#--------------------------------------------------------------------------
#This library is free software; you can redistribute it and/or
#modify it under the terms of the GNU Lesser General Public
#License as published by the Free Software Foundation; either
#version 2.1 of the License, or (at your option) any later version.

#This library is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
#Lesser General Public License for more details.

#You should have received a copy of the GNU Lesser General Public
#License along with this library; if not, write to the Free Software
#Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA

from gnr.core.gnrdecorator import public_method

class AppPref(object):
    def permission_glbl(self, **kwargs):
        return 'admin'
    def prefpane_glbl(self, parent, **kwargs):
        pane = parent.contentPane(**kwargs)
        fb = pane.formbuilder(cols=1,border_spacing='3px')
        #fb.button('Dump GLBL',action='PUBLISH dump_glbl')
        fb.button('Restore GLBL',action='PUBLISH restore_glbl')
        #fb.dataRpc('dummy',self._glbl_dumpPickle,subscribe_dump_glbl=True,_lockScreen=True)
        fb.dataRpc('dummy',self._glbl_loadPickle,subscribe_restore_glbl=True,timeout=0,_onCalling="genro.mainGenroWindow.genro.publish('open_batch');")


    @public_method
    def _glbl_dumpPickle(self):
         self.db.package('glbl').pickleAllData()
         
    @public_method
    def _glbl_loadPickle(self):
        pkg = self.db.package('glbl')
        self.btc.batch_create(title='Glbl Importer',
                              cancellable=True,
                              delay=.5)
        pkg.unpickleAllData(btc=self.btc)
        self.btc.batch_complete(result='ok', result_attr=dict())

