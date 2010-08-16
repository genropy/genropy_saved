# -*- coding: UTF-8 -*-

# thermopane.py
# Created by Francesco Porcari on 2010-08-13.
# Copyright (c) 2010 Softwell. All rights reserved.

import time

class GnrCustomWebPage(object):
    py_requires='gnrcomponents/thermopane:ThermoPane'


    def windowTitle(self):
        return 'ThermoPane'
         
    def main(self, root, **kwargs):   
        bc = root.borderContainer() 
        top = bc.contentPane(region='top')
        top.button('Start',fire='start_test')        
        center = bc.contentPane(region='center') 
        center.data('thermo.status?hidden',True)
        self.thermoPane(center,title='test',nodeId='test',datapath='thermo',items='test')
        root.dataController("""SET thermo.status?hidden=false; FIRE run_rpc;""",_fired="^start_test")
        root.dataRpc('dummy','test_thermo',_fired='^run_rpc',_onCalling='genro.rpc.managePolling(.5);',
                    _onResult='genro.rpc.managePolling(null);')
            
    def rpc_test_thermo(self):
        self.update_thermo('thermo','test',progress=0,maximum=100,message='Starting...')
        
        for k in range(100):
            time.sleep(.4)
            self.update_thermo('thermo','test',progress=k,maximum=100,message='working %i' %k,)
            
    def update_thermo_(self,thermo_path,thermo_item,progress=None,message=None,maximum=None):
        self.site.setInClientPage(client_path='%s.items.%s' %(thermo_path,thermo_item),
                        attributes=dict(progress=progress,message=message,maximum=maximum),saveSession=True)
                        
    def update_thermo(self,thermo_path,thermo_item,progress=None,message=None,maximum=None):
        pass
