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

"""
Component for thermo:
"""
from gnr.web.gnrbaseclasses import BaseComponent
from gnr.core.gnrbag import Bag
import time

class Thermo(BaseComponent):
    def thermoNewDialog(self, pane, thermoId='thermo', title='', thermolines=1, fired=None, pollingFreq=1):
        dlgid = 'dlg_%s' % thermoId
        d = pane.dialog(nodeId=dlgid, title=title, width='27em', datapath='_thermo.%s' % thermoId,
                        closable='ask', close_msg='!!Stop the batch execution?', close_confirm='Stop',
                        close_cancel='Continue',
                        close_action='genro.setInServer("thermo_%s_stop", true);' % thermoId)
        for x in range(thermolines):
            tl = d.div(datapath='.t.t%i' % (x, ))
            tl.progressBar(width='25em', indeterminate='^.indeterminate', maximum='^.maximum',
                           places='^.places', progress='^.progress', margin_left='auto', margin_right='auto')
            tl.div('^.message', height='1em', text_align='center')
        d.div(width='100%', height='4em').div(margin='auto').button('Stop',
                                                                    action='genro.wdgById("%s").onAskCancel();' % dlgid)

        pane.dataController('genro.wdgById(dlgid).show();genro.setFastPolling(true)', dlgid=dlgid,
                            fired=fired) # genro.rpc.setPolling(%s);  % pollingFreq
        pane.dataController('genro.wdgById(dlgid).hide();genro.setFastPolling(false)', dlgid=dlgid,
                            _fired='^_thermo.%s.c.end' % thermoId) # genro.rpc.setPolling();


    def setNewThermo(self, thermoId, level, progress, maximum, message='', indeterminate=False, lazy=True):
        #lazy: send to client at most 1 value change per second. 
        #Subsequent calls to setNewThermo in the next second are ignored
        end = (level == -1 or (level == 0 and progress >= maximum))
        if end:
            self.setInClientData('_thermo.%s.c.end' % thermoId, True, fired=True, page_id=self.page_id, public=True)
            with self.pageStore() as store:
                if store.get('thermo_%s_stop' % thermoId):
                    store.setItem('thermo_%s_stop' % thermoId, None)

        now = time.time()

        if not hasattr(self, 'lastThermoUpdTime'):
            self.lastThermoUpdLevel = None
            self.lastThermoUpdTime = 0

        if lazy and level == self.lastThermoUpdLevel and now - self.lastThermoUpdTime < 1:
            return
        self.lastThermoUpdTime = now
        self.lastThermoUpdLevel = level

        tbag = Bag(dict(progress=progress, maximum=maximum, message=message, indeterminate=indeterminate))
        self.setInClientData('_thermo.%s.t.t%s' % (thermoId, level), tbag, page_id=self.page_id, public=True)
        store=self.pageStore()
        if store.get('thermo_%s_stop' % thermoId):
            return True
        else:
            return False
            