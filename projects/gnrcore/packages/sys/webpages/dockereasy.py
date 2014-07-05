#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#
#  untitled
#
#  Created by Giovanni Porcari on 2007-03-24.
#  Copyright (c) 2007 Softwell. All rights reserved.
#

DOCKER_IP = '192.168.59.103'
from gnr.core.gnrdecorator import public_method
from gnr.core.gnrbag import Bag
from gnr.core.gnrstring import fromJson
from datetime import datetime,timedelta
from docker.client import Client


class GnrCustomWebPage(object):
    css_requires='public'
    py_requires='gnrcomponents/framegrid:FrameGrid,gnrcomponents/formhandler:FormHandler'

    def main(self, root, **kwargs):
        bc = root.borderContainer(datapath='main')
        top = bc.tabContainer(region='top',height='250px',splitter=True,margin='2px')
        self.imagesFrame(top.contentPane(title='Images'))
        self.commandsFrame(top.contentPane(title='Commands',datapath='.commands'))
        self.containerFrame(top.contentPane(title='Container'))
        bc.contentPane(region='center')

    def imagesFrame(self,pane):
        frame = pane.frameGrid(frameCode='dockerImages',datapath='.images',
                      struct=self.struct_images)
        frame.top.slotToolbar('2,vtitle,*,delrow,searchOn,4',vtitle='Images')
        frame.grid.bagStore(storeType='ValuesBagRows',
                                sortedBy='=.grid.sorted',
                                deleteRows="""function(pkeys,protectPkeys){
                                                    var that = this;
                                                    genro.serverCall('deleteImages',{imagesNames:pkeys},
                                                                    function(){
                                                                        that.loadData();
                                                                    });
                                                }""",
                                data='^.currentImages',selfUpdate=True,
                                _identifier='Id')
        frame.dataRpc('.currentImages',self.getCurrentImages,_onStart=True,_timing=5)

    @public_method
    def deleteImages(self,imagesNames=None):
        docker = self.docker
        for imgname in imagesNames:
            docker.remove_image(imgname,force=True)

    def struct_images(self,struct):
        r = struct.view().rows()
        r.cell('RepoTags',width='15em',name='RepoTags')
        r.cell('Created', width='6em', name='Created')
        r.cell('Id', width='20em', name='Id')
        r.cell('ParentId', width='20em', name='ParentId')
        r.cell('Size',width='10em',name='Size')
        r.cell('VirtualSize',width='10em',name='VirtualSize')

        #{"Created":1404384367,
        #"Id":"451ad2d487565d182dd18efdf751cf657c68943c7694095e9d772e06fdc403a5",
        #"ParentId":"f202f5e89f17dc62b30950eeb85c5cb5be172118180b0a57ea8effed129e10aa",
        #"RepoTags":["\u003cnone\u003e:\u003cnone\u003e"],
        #"Size":29858431,"VirtualSize":518328399}

    @public_method
    def startSelectedContainers(self,pkeys=None):
        for contId in pkeys:
            self.docker.start(contId,publish_all_ports=True)

    @public_method
    def stopSelectedContainers(self,pkeys=None):
        for contId in pkeys:
            self.docker.stop(contId)

    @public_method
    def removeSelectedContainers(self,pkeys=None):
        for contId in pkeys:
            self.docker.remove_container(contId)

    def containerFrame(self,pane):
        frame = pane.frameGrid(frameCode='containers',datapath='.containers',struct=self.struct_containers)
        bar = frame.top.slotToolbar('2,sbuttons,*,stop_remove_btn,start_btn,searchOn,4')
        bar.start_btn.slotButton('Start',hidden='^.currentStorename?=#v=="active"',action='FIRE .start_selected')
        bar.stop_remove_btn.slotButton('Stop',hidden='^.currentStorename?=#v=="exited"',action='FIRE .stop_selected')
        bar.stop_remove_btn.slotButton('Remove',hidden='^.currentStorename?=#v=="active"',action='FIRE .remove_selected')
        bar.sbuttons.multiButton(value='^.currentStorename',values='active:Active containers,exited:Exited containers')
        rpckw = dict(_grid=frame.grid.js_widget,
                    _onCalling='kwargs["pkeys"]=_grid.getSelectedPkeys()',
                    _onResult='FIRE .forced_reload;')
        bar.dataRpc('dummy',self.startSelectedContainers,_fired='^.start_selected',**rpckw)
        bar.dataRpc('dummy',self.stopSelectedContainers,_fired='^.stop_selected',_ask='You are stopping some containers. Confirm?',**rpckw)
        bar.dataRpc('dummy',self.removeSelectedContainers,_fired='^.remove_selected',_ask='You are removing some containers. Confirm?',**rpckw)

        frame.grid.bagStore(storeType='ValuesBagRows',
                                sortedBy='=.grid.sorted',
                                data='^.currentStoreData',selfUpdate=True,
                                _identifier='Id')
        bar.dataController("""
                            var currentStoreData = data.getItem(currentStorename);
                            SET .currentStoreData = currentStoreData?currentStoreData.deepCopy():new gnr.GnrBag();""",
                            data='^.containerData',currentStorename='^.currentStorename',_delay=100)
        frame.dataRpc('.containerData',self.getContainers,_onStart=True,_timing=5,_fired='^.forced_reload')

    def commandsFrame(self,pane):
        view = pane.frameGrid(frameCode='V_commands' ,struct=self.struct_command,
                                    datapath='.view')
        view.top.slotToolbar('2,vtitle,*,delrow,addrow,5',vtitle='Commands')
        fstore = view.grid.fsStore(childname='store',
                                    folders='site:docker/commands',
                                    include='*.xml')
        view.dataController("fstore.store.loadData();",fstore=fstore,_onBuilt=True)
        form = view.grid.linkedForm(frameCode='F_commands',
                                 datapath='.form',loadEvent='onRowDblClick',
                                 dialog_height='450px',dialog_width='620px',
                                 modal=True,
                                 dialog_title='Command',
                                 handlerType='dialog',
                                 childname='form',attachTo=pane,
                                 store='document')
        form.store.handler('save',rpcmethod=self.saveCommand)

        fb = form.record.formbuilder(cols=2,border_spacing='3px')
        form.top.slotToolbar('2,navigation,*,delete,add,save,semaphore,2')

        fb.textbox(value='^.dockerpath',lbl='Docker image')
        fb.checkbox(value='^.daemon',lbl='Daemon')
        fb.checkbox(value='^.open_port',lbl='Open ports')

    @public_method
    def saveCommand(self,data=None,**kwargs):
        p = self.site.getStaticPath('site:docker','containers','%s.xml' %data['dockerpath'].replace('/','_'),autocreate=-1)
        data.toXml(p)

    def struct_command(self,struct):
        r = struct.view().rows()
        r.cell('dockerpath')
        r.cell('daemon')
        r.cell('open_port')

    @public_method
    def getCurrentImages(self):
        result = Bag()
        result.fromJson(self.docker.images(),listJoiner=',')
        return result

    @public_method
    def getContainers(self):
        result = Bag()
        for i,cnt in enumerate(self.docker.containers(all=True)):
            #0.0.0.0:49153->8080/tcp
            r = Bag(cnt)
            r['Names'] = ','.join(r['Names'])
            r['Ports'] = ','.join(['%(IP)s:%(PublicPort)s->%(PrivatePort)s/%(Type)s' %kw for kw in r['Ports']])
            if 'Exited' in r['Status']:
                prefix = 'exited'
            else:
                prefix = 'active'
            result.setItem('%s.r_%i' %(prefix,i),r)
        return result

    @property
    def docker(self):
        if not getattr(self,'_dockerclient',None):
            self._dockerclient = Client('tcp://%s:2375' %DOCKER_IP)
        return self._dockerclient

    def struct_containers(self,struct):
        r = struct.view().rows()
        r.cell('Command',width='12em',name='Command')
        r.cell('Created',width='12em',name='Created')
        r.cell('Id',width='20em',name='Id')
        r.cell('Image',width='20em',name='Image')
        r.cell('Names',width='20em',name='Names')
        r.cell('Ports',width='20em',name='Ports')
        r.cell('Status',width='12em',name='Status')




