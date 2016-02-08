# -*- coding: UTF-8 -*-
from gnr.core.gnrdecorator import websocket_method, public_method
from gnr.core.gnrbag import Bag


class GnrCustomWebPage(object):
    
    def isDeveloper(self):
        return True

    def main(self,root,room=None,**kwargs):
        frame = root.framePane(datapath='main')
        self.mainToolbar(frame.top,room=room,datapath='.roomselector')
        bc = frame.center.borderContainer()
        self.fieldsPane(bc.contentPane(datapath='.shared.info',region='left',border_right='1px solid silver',splitter=True))
        self.drawingPane(bc.contentPane(region='center'))
        
    def mainToolbar(self,pane,room=None,datapath=None):
        bar=pane.slotToolbar(slots='rooms,20,savebtn,*',datapath=datapath)
        bar.dataController('SET .room=room',_onStart=True,room=room or 'collaborative_test')
        bar.savebtn.slotButton('Save',action='genro.wsk.saveSharedObject(room);',room='=.room')
        fb=bar.rooms.formbuilder(cols=3,border_spacing='0')
        fb.textbox(value='^.room',lbl='Room')
        bar.dataController("""if (old_room){genro.som.unregisterSharedObject(old_room);};
                               genro.som.registerSharedObject('main.shared',room,{expire:20,autoSave:true,autoLoad:true});
                              SET .old_room=room;
                             """,room='^.room',old_room='=.old_room',_if='room')
                         
    def fieldsPane(self,pane):
        fb = pane.div(padding='10px').formbuilder(cols=1,border_spacing='3px')
        fb.textbox(value='^.alfa',lbl='Alfa')
        fb.textbox(value='^.beta',lbl='Beta')
        fb.textbox(value='^.gamma',lbl='Gamma')
        fb.textbox(value='^.delta',lbl='Delta')
        fb.dataController("""console.log('_triggerpars',_triggerpars)
            var result=[alfa,beta,gamma,delta].join('<br/>');
            SET .result=result;
        """,alfa='^.alfa',
                           beta='^.beta',gamma='^.gamma',delta='^.delta')
        fb.dataController("""console.log('resulttrigger',_triggerpars)""",_fired='^.result')
        fb.div('^.result',lbl='result')
        pane.simpletextarea('^.testo',width='200px',height='130px',lbl='testo',moveable=True)

    def drawingPane(self,bc):
        bc.dataController(datapath='.shared.drawing.elements',nodeId='elements')
        center = bc.contentPane(region='center',
                               #datapath='.shared.drawing.data',
                               connect_ondblclick="""

            if($1.shiftKey){
                var that = this;
                var dflt = new gnr.GnrBag({tag:'div',name:'box_'+genro.getCounter(),
                                           value:'',
                                           height:'100px',
                                           width:'100px',
                                           background:'red',
                                           border:'1px solid silver',
                                           moveable:true,
                                           position:'absolute',
                                           start_x:$1.offsetX,start_y:$1.offsetY});
                genro.dlg.prompt('Create',{widget:'multiValueEditor',
                                            dflt:dflt,
                                            action:function(result){
                                                var path='#elements.'+result.getItem('name')
                                                 that.setRelativeData(path,result.deepCopy());    
                                            }
                                });
            }
        
        """)
        bc.dataController("""
            var createNode=function(pane,pars){
                var kw = pars.asDict();
                var start_x = objectPop(kw,'start_x');
                var start_y = objectPop(kw,'start_y');               
                var tag = objectPop(kw,'tag') || 'div';
                var name = objectPop(kw,'name') || 'box_'+genro.getCounter();
                if(kw.moveable){
                    kw.position = 'absolute';
                    kw.top = '^#elements.'+name+'.top';
                    kw.left = '^#elements.'+name+'.left';
                    genro.setData(kw.top ,start_y+'px');
                    genro.setData(kw.left ,start_x+'px');
                }else{
                    if(kw.position=='absolute' || kw.position=='relative'){
                        kw.top  = start_y+'px';
                        kw.left  = start_x+'px'
                    }
                }
                pane._(tag,name,kw);
            }
            var tkw=_triggerpars.kw
          if (_reason=='container'){
              elements.forEach(function(n){
                 createNode(pane,n.getValue())
                } 
              )
          }
            if (tkw.where != elements) {
                return
            }
            if (tkw.evt=='ins'){
               createNode(pane,_node.getValue())
            }else if (tkw.evt=='del'){
                pane.popNode(_node.label)
            }else{
            genro.bp(true)
            }
            """,pane=center,elements='^#elements',_if='elements'
        )
        