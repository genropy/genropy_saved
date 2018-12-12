# -*- coding: utf-8 -*-
from gnr.core.gnrdecorator import websocket_method, public_method

class GnrCustomWebPage(object):
    
    def isDeveloper(self):
        return True

    def main(self,root,**kwargs):
        bc = root.borderContainer(height='100%',datapath='main')
        top = bc.contentPane(region='top', height='100px',border_bottom='1px solid silver')
        self.topPane(top)
        center=bc.contentPane(region='center').pre(id='rpdb_log')
        bottom=bc.contentPane(region='bottom',height='50px',splitter=True)
        self.bottomPane(bottom)
        
    def topPane(self,top):
        top.dataController("""
          genro.rpdb_ws = new ReconnectingWebSocket(url)
          
          genro.rpdb_ws.onopen = function() {
              genro.bp(true)
            genro.publish('rpdb_log','CONNECT');
          };
          genro.rpdb_ws.onclose = function() {
            genro.publish('rpdb_log','DISCONNECT');
          };
          genro.rpdb_ws.onmessage = function(event) {
              genro.publish('rpdb_log',event.data);
          };
          """,url="ws://localhost:8080/",_onStart=True)
        top.dataController("""
            genro.bp(true)
            document.getElementById('rpdb_log').textContent += $1 + '\n';
        """,subscribe_rpdb_log=True)
        
    def bottomPane(self,bottom):
        fb=bottom.div(top='4px',bottom='4px',left='4px',
                   right='4px',position='absolute',font_family='courier').formbuilder(cols=2)
        fb.div(lbl='!!Command',width='100%').simpletextarea(value='^.content',width='100%',height='100%')
        fb.dataController("""genro.rpdb_ws.send(command+'\n')""",command='^.commandToSend')
        fb.button(label='Send',width='70px',action="""
                            var command = GET .command;
                            SET .commandToSend = command
                            genro.publish('rpdb_log',command);
                            SET .command='';
                            """)

        
        
