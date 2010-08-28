# -*- coding: UTF-8 -*-

# thermopane.py
# Created by Francesco Porcari on 2010-08-13.
# Copyright (c) 2010 Softwell. All rights reserved.

import os
from gnr.core.gnrbag import Bag
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
        root.dataRpc('dummy','test_thermo',_fired='^run_rpc',_onCalling='genro.rpc.managePolling(.5);'
                    ,_onResult='console.log("finished");console.log(result)')
        top.dataController('if(value==20){genro.rpc.managePolling(null);}',value='^thermo.items.test')
            
    def rpc_test_thermo(self):
        request=self.request._request
        protocol = request.host_url.split('//')[0]
        host = '%s//localhost' % protocol
        if ':' in request.host:
            port = request.host.split(':')[1]
            host = '%s:%s' %(host,port)
        url = '%s%s?method=' %(host,request.path_info)

        print x
        if not request.user_agent.startswith('curl'):
            os.system("""nohup curl "%s" -o "%s" &""" %(request.url,'/result.txt'))
            return
        t = time.time()
        self.update_thermo('thermo','test',progress=0,maximum=200,message='Starting...')
        for k in range(201):
            time.sleep(.4)
            self.update_thermo('thermo','test',progress=k,maximum=200,message='working %i' %k)
        time.sleep(1)
        result = Bag()
        result['esito'] = 'done'
        result['tempo'] =str(time.time()-t)
        print 'ok'
        return result
        
        
       
       #result['url'] = request.url
       #result['user_agent'] =  request.user_agent
        #print x
        #return result
        
    def rpc_test_thermo_(self):
        os.system('nohup curl http://www.istruzionefc.it/uopsa/public/articoli/allegati/angella.pdf > $HOME/angella.pdf &')
        
        # self.response.write('200 pippo'+chr(12)+chr(10))
        # self.update_thermo('thermo','test',progress=0,maximum=20,message='Starting...')
        # for k in range(21):
        #     time.sleep(.4)
        #     self.update_thermo('thermo','test',progress=k,maximum=20,message='working %i' %k)
            
    def update_thermo(self,thermo_path,thermo_item,progress=None,message=None,maximum=None):
        self.setInClientData(path='%s.items.%s' %(thermo_path,thermo_item),value=progress,page_id=self.page_id,
                             attributes=dict(progress=progress,message=message,maximum=maximum),
                             public=True,replace=True)
                        
