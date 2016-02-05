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
        #self.drawingPane(bc.contentPane(region='center'))
        bc.dataController(datapath='.shared.elements',nodeId='elements')
        center = bc.contentPane(region='center',connect_ondblclick="""

            if($1.shiftKey){
                var that = this;
                var dflt = new gnr.GnrBag({tag:'div',name:'box_'+genro.getCounter(),
                                           border:'1px solid silver',
                                           position:'absolute',
                                           height:'100px',
                                           width:'100px',
                                           background:'red',
                                           moveable:true,
                                           start_x:$1.x,start_y:$1.y});
                genro.dlg.prompt('Create',{widget:'multiValueEditor',
                                            dflt:dflt,
                                            action:function(result){
                                                 that.setRelativeData('.shared.command',result.deepCopy());    
                                            }
                                });
            }
        
        """)
        bc.dataController("""
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
            """,pane=center,pars='^.shared.command',_if='pars'
        )
        
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
       # fb.button('Save',action='genro.wsk.saveSharedObject(room);',room=room)

        #fb.button('Load',action='genro.wsk.loadSharedObject(room);',room=room)

        #fb.button('Subscribe',action="""
        #    genro.som.registerSharedObject('main.shared','collaborative_test',{expire:20})""")
#
        #fb.button('Unregister',action="""
        #    genro.som.unregisterSharedObject(room);
        #""",room=room)
#

    def drawingPane(self,pane):
        
        fp=parent.framePane(region='bottom',height='50%')
        fp.center.attributes.update(datapath='.dd.drawing')
        fp.dataController("""center._('')""",
                          center=fp.center,
                           subscribe_makeElement=True)
         
        bar=fp.top.slotBar(slots='make')
        # bar.make.slotButton(action="""genro.publish('makeElement',{tag:'div',position:'absolute',
        #                                                           top:'^.abj.top',
        #                                                           left:'^.obj.left',
        #                                                           background='red'
       #                                                      })""")
       #center=bc.contentPane(region='center',datapath='.shggared.info')
       #center.data('.box',Bag(dict(top='100px',left='100px')))
       #m=center.div(position='absolute',border='1px solid red',datapath='.box',
       #                 top='^.top',width='100px',height='100px',left='^.left',
       #                     background='yellow',moveable=True)
       #m.div('^.top')
       #m.div('^.left')
       #
