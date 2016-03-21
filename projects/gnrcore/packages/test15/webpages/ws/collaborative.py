# -*- coding: UTF-8 -*-
from gnr.core.gnrdecorator import websocket_method, public_method
from gnr.core.gnrbag import Bag


class GnrCustomWebPage(object):
    
    py_requires='gnrcomponents/workbench/workbench:WorkbenchManager'
    
    def isDeveloper(self):
        return True

    def main(self,root,room=None,**kwargs):
        frame = root.framePane(datapath='main')
        self.mainToolbar(frame.top,room=room,datapath='.roomselector')
        bc = frame.center.borderContainer()
        self.fieldsPane(bc.borderContainer(datapath='.shared.info',region='left',border_right='1px solid silver',splitter=True))
        bc.workbenchPane('elements',region='center',datapath='.shared.drawing.elements')
        
    def mainToolbar(self,pane,room=None,datapath=None):
        bar=pane.slotToolbar(slots='rooms,20,savebtn,*',datapath=datapath)
        bar.dataController('SET .room=room',_onStart=True,room=room or 'collaborative_test')
        bar.savebtn.slotButton('Save',action='genro.som.saveSharedObject(room);',room='=.room')
        fb=bar.rooms.formbuilder(cols=3,border_spacing='0')
        fb.textbox(value='^.room',lbl='Room')
        bar.dataController("""if (old_room){genro.som.unregisterSharedObject(old_room);};
                               genro.som.registerSharedObject('main.shared',room,{expire:20,autoSave:true,autoLoad:true});
                              SET .old_room=room;
                             """,room='^.room',old_room='=.old_room',_if='room')
                         
    def fieldsPane(self,bc):
        pane=bc.contentPane(region='top')
        fb = pane.div(padding='10px').formbuilder(cols=1,border_spacing='3px')
        fb.textbox(value='^.alfa',lbl='Alfa')
        fb.textbox(value='^.beta',lbl='Beta')
        fb.textbox(value='^.gamma',lbl='Gamma')
        fb.textbox(value='^.delta',lbl='Delta')
        fb.dataController("""
            var result=[alfa,beta,gamma,delta].join('<br/>');
            SET .result=result;
        """,alfa='^.alfa',
                           beta='^.beta',gamma='^.gamma',delta='^.delta')
        fb.dataController("""console.log('resulttrigger',_triggerpars)""",_fired='^.result')
        fb.div('^.result',lbl='result')
        center=bc.contentPane(region='center',moveable_constrain=True,
                selfsubscribe_moveable_created="console.log('moveable_created',$1);",
                selfsubscribe_moveable_moved="console.log('moveable_moved',$1);")
        
        center.simpletextarea('^.testo',width='200px',height='130px',lbl='testo',
                            moveable=True)


        