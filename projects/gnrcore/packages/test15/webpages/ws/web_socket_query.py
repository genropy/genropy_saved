# -*- coding: utf-8 -*-


from builtins import object
class GnrCustomWebPage(object):
    def main(self,root,**kwargs):
        root.script("""genro.ws=gnrwebsocket;
                       genro.ws.create('ws://'+window.location.host+'/websocket')""")
        bc=root.borderContainer(height='100%')

        top=bc.contentPane(height='150px',background='#eee')
        fb=top.formbuilder(cols=1,datapath='test') 
        fb.h1('test query')
        fb.textbox(value='^.table',lbl='Table')
        fb.textbox(value='^.pkey',lbl='Pkey')
        fb.div('^received.text')
        fb.dataController("""genro.ws.send('getRecord',{
                                    'table':table,
                                    'pkey':pkey,
                                    'dest_path':'received.records.'+pkey
                                    })""",
                       table='^.table',pkey='^.pkey',_if='table&&pkey')
        
        center=bc.contentPane(background='#eee')
        trees=center.table(height='100%',width='100%',background='#eee').tbody().tr()
        center.dataController("""var kw=_triggerpars.kw;
                             if(kw.evt=='ins' && kw.where==records){
                                 var value=_node.value;
                                 var box=trees._('td',{'valign':'top'})._('div',{'border':'1px solid #ddd'})
                                 box._('div',{'height':'14px','border_bottom':'1px solid #ddd','padding':'4px','innerHTML':_node.attr.caption})
                                 box._('div',{'padding':'4px'} )._('tree',{'storepath':'received.records.'+_node.label})
                             }
                             """,
                       records='^received.records',
                       trees=trees)
        
                
        
        
  
        
