# -*- coding: utf-8 -*-
from builtins import range
from builtins import object
from gnr.core.gnrdecorator import websocket_method, public_method
from gnr.core.gnrbag import Bag

class GnrCustomWebPage(object):
    
    def isDeveloper(self):
        return True

    def main(self,root,**kwargs):
        bc = root.borderContainer(height='100%',datapath='main')
        top = bc.contentPane(region='top', height='400px',border_bottom='1px solid silver')
        fb=top.formbuilder(cols=3)
        fb.data('.dest_page_id',self.page_id)
        fb.data('.client_path','main.result')
        fb.data('.result_stress','')
        fb.data('.data','Prova Dati')

        fb.textBox(value='^.dest_page_id',lbl='Page id')
        fb.textBox(value='^.client_path',lbl='Client path')
        fb.textBox(value='^.data',lbl='Data',colspan=2)
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
        
    @public_method
    def sendToPage(self,dest_page_id=None,data=None,client_path=None,**kwargs):
        self.wsk.sendCommandToPage(dest_page_id,'set',Bag(dict(path=client_path,data=data)))
        
    @public_method
    def stressToPage(self,dest_page_id=None,data=None,client_path=None,**kwargs):
        for k in range(10):
            self.wsk.sendCommandToPage(dest_page_id,'set',Bag(dict(path=client_path,
                                data='%s %i'%(data,k))))

        
        
        
