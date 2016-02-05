# -*- coding: UTF-8 -*-
from gnr.core.gnrdecorator import websocket_method, public_method
from gnr.core.gnrbag import Bag


class GnrCustomWebPage(object):
    
    def isDeveloper(self):
        return True

    def main(self,root,room=None,**kwargs):
        bc = root.borderContainer(datapath='main')
        self.mainToolbar(bc.contentPane(datapath='.roomselector',region='top'),room=room)
        self.fieldsPane(bc.contentPane(datapath='.shared.info',region='left',width='30%',splitter=True))
        #self.drawingPane(bc.contentPane(region='center'))
        center = bc.contentPane(region='center',connect_ondbclick="""
            if($1.shiftKey){
                console.log('aaa',$1)
            }
        
        """)
        bc.dataController("""objectUpdate({},_subscription_kwargs);""",
                            pane=center,
                            subscribe_drawElement=True)
        
    def mainToolbar(self,pane,room=None):
        bar=pane.slotToolbar(slots='rooms,20,savebtn,*',datapath=datapath)
        bar.dataController('SET .room=room',_onStart=True,room=room or 'collaborative_test')
        bar.savebtn.slotButton('Save',action='genro.wsk.saveSharedObject(room);',room='=.room')
        fb=bar.rooms.formbuilder(cols=3)
        fb.textbox(value='^.room',lbl='Room')
        
        bar.make.slotButton("Make")
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
