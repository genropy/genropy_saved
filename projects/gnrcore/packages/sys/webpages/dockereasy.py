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
    py_requires='gnrcomponents/framegrid:FrameGrid'

    def main(self, root, **kwargs):
        bc = root.borderContainer(datapath='main')
        top = bc.stackContainer(region='top',height='250px',splitter=True)
        self.imagesFrame(top.contentPane(title='Images'))
        self.processFrame(top.contentPane(title='Process'))
        bc.contentPane(region='center')

    def imagesFrame(self,pane):
        frame = pane.frameGrid(frameCode='dockerImages',datapath='.images',
                      struct=self.struct_images)
        frame.top.slotToolbar('2,parentStackButtons,*,delrow,searchOn,4')
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
        frame.dataRpc('.currentImages',self.getCurrentImages,_onStart=True,_timing=5000)

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

    def processFrame(self,pane):
        frame = pane.frameGrid(frameCode='processImages',datapath='.process',
                      struct=self.struct_process)
        frame.top.slotToolbar('2,parentStackButtons,*,searchOn,4')
        frame.grid.bagStore(storeType='ValuesBagRows',
                                sortedBy='=.grid.sorted',
                                data='^.currentProcess',selfUpdate=True,
                                _identifier='Id')
        frame.dataRpc('.currentProcess',self.getCurrentProcess,_onStart=True,_timing=5000)

    @public_method
    def getCurrentImages(self):
        result = Bag()
        result.fromJson(self.docker.images(),listJoiner=',')
        return result

    @public_method
    def getCurrentProcess(self):
        result = Bag()
        for i,cnt in enumerate(self.docker.containers()):
            #0.0.0.0:49153->8080/tcp
            r = Bag(cnt)
            r['Names'] = ','.join(r['Names'])
            r['Ports'] = ','.join(['%(IP)s:%(PublicPort)s->%(PrivatePort)s/%(Type)s' %kw for kw in r['Ports']])
            result.setItem('r_%i' %i,r)
        return result

    @property
    def docker(self):
        if not getattr(self,'_dockerclient',None):
            self._dockerclient = Client('tcp://%s:2375' %DOCKER_IP)
        return self._dockerclient

    def struct_process(self,struct):
        r = struct.view().rows()
        r.cell('Command',width='12em',name='Command')
        r.cell('Created',width='12em',name='Created')
        r.cell('Id',width='20em',name='Id')
        r.cell('Image',width='20em',name='Image')
        r.cell('Names',width='20em',name='Names')
        r.cell('Ports',width='20em',name='Ports')
        r.cell('Status',width='12em',name='Status')




