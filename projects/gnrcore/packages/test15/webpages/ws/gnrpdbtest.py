# -*- coding: utf-8 -*-
from gnr.core.gnrdecorator import websocket_method, public_method
from gnr.core.gnrbag import Bag
import rpdb

class GnrCustomWebPage(object):
    
    def isDeveloper(self):
        return True

    def main(self,root,**kwargs):
        bc = root.borderContainer(height='100%',datapath='main')
        top = bc.contentPane(region='top', height='400px',border_bottom='1px solid silver')
        center = bc.borderContainer(region='center', border_bottom='1px solid silver', datapath='.debugger')
        self.debuggerPane(center)
        fb=top.formbuilder(cols=3)
        fb.data('.dest_page_id',self.page_id)
        fb.data('.client_path','main.result')
        fb.data('.result_stress','')
        fb.data('.data','Prova Dati')

        fb.textBox(value='^.dest_page_id',lbl='Page id')
        fb.textBox(value='^.client_path',lbl='Client path')
        fb.textBox(value='^.data',lbl='Data',colspan=2)
        fb.button('focusdebug',action='genro.dev.startDebug();')

        fb.button('Send',fire='.send')
        
        fb.div('^.result',lbl='Result',colspan=2)
        fb.button('Stress',fire='.stress')
        fb.div('^.result_stress',lbl='Result',colspan=2)
        
        
        
        fb.dataRpc('.dummy',self.sendToPage,dest_page_id='=.dest_page_id',
                                client_path='=.client_path',data='=.data',_fired='^.send')
                                
        fb.dataRpc('.dummy',self.stressToPage,dest_page_id='=.dest_page_id',
                                client_path='main.result_one',data='=.data',_fired='^.stress')
                                
        fb.dataController("""SET .result_stress=curr+'<br/>'+one """
                          ,one='^.result_one',curr='=.result_stress')
        fb.button('testdebug',fire='.testdebug')
        
                                   
        fb.dataRpc('.dummy',self.testdebug,_fired='^.testdebug',
            _onResult='alert("finito")',timeout=3000)
        
        
    def debuggerPane(self, bc):
        bottom = bc.contentPane(region='bottom', height='10ex')
        center = bc.contentPane(region='center')
        fb_bottom = bottom.formbuilder(cols=2)
        fb_bottom.textBox(lbl='Command',value='^.command', nodeId='commandField',
                    connect_onkeyup="""
                                      var target = $1.target;
                                      var value = $1.target.value;
                                      var key = $1.keyCode;
                                      if(key==13){
                                         var cmd = value.replace(_lf,"");
                                         genro.wsk.send("debugcommand",{cmd:cmd});
                                         $1.target.value = null;
                                      }""")
        
        fb_bottom.button('Send', action='genro.wsk.send("debugcommand",{cmd:cmd}); SET .command=null;', cmd='=.command')
        out_div = center.div('^.output', style='font-family:monospace; white-space:pre;')
        center.dataController("""console.log('dataController', data);            SET .output = output+_lf+data""",output='=.output',
            subscribe_fromdebugger=True)


    @public_method
    def sendToPage(self,dest_page_id=None,data=None,client_path=None,**kwargs):
        self.wsk.sendCommandToPage(dest_page_id,'set',Bag(dict(path=client_path,data=data)))
        
    @public_method
    def stressToPage(self,dest_page_id=None,data=None,client_path=None,**kwargs):
        for k in range(10):
            self.wsk.sendCommandToPage(dest_page_id,'set',Bag(dict(path=client_path,
                                data='%s %i'%(data,k))))

    @public_method
    def testdebug(self,**kwargs):
        #self.pdb.set_trace()
        a=45
        b=67
        for k in range (10):
            s=self.somma(a,b)
        return s
    
    def somma(self,a,b):
        a=a*5
        b=b*5
        z = Bag(dict(risultato=a+b))
        m = [1,4,6,'pippo']
        return a+b
    
        
        
