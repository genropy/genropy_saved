#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#
#  untitled
#
#  Created by Giovanni Porcari on 2007-03-24.
#  Copyright (c) 2007 Softwell. All rights reserved.
#
from gnr.core.gnrdecorator import public_method
from gnr.core.gnrbag import Bag


class GnrCustomWebPage(object):

    py_requires='gnrcomponents/framegrid:FrameGrid'


    def windowTitle(self):
        return '!!Register explorer'

    def sitesStruct(self,struct):
        r = struct.view().rows()
        r.cell('sitename', width='20em',name='Site name')
        r.cell('uri',width='10em',name='Site uri')
        r.cell('start_ts',width='10em',name='Started')

    def main(self, root, **kwargs):
        bc = root.borderContainer(datapath='main')
        bc.dataFormula('.refreshtime','timing',timing=5,_onStart=True)
        frame = bc.frameGrid(frameCode='runningSites',region='left',datapath='runningSites',
                   width='400px',struct=self.sitesStruct,_class='pbl_roundedGroup',
                   grid_selected_sitename='main.sitename',grid_selected_uri='main.uri')

        frame.grid.bagStore(storepath='runningSites.store',storeType='AttributesBagRows',
                                sortedBy='=.grid.sorted',
                                data='^runningSites.loaded_data',selfUpdate=True)
        bc.dataRpc('runningSites.loaded_data',self.runningSites,_timing='^.refreshtime')
        bc.dataRpc('dummy',self.daemonCommands,command='^runningSites.command',sitename='=main.sitename')
        frame.top.slotBar('2,vtitle,*',vtitle='Running sites',_class='pbl_roundedGroupLabel')
        self.centerpane(bc.borderContainer(region='center'))

    def centerpane(self,bc):
        top = bc.contentPane(region='top',height='150px',background='silver')
        fb = top.formbuilder(cols=1,border_spacing='3px')
        fb.div('^main.sitename')
        fb.div('^main.uri')
        fb.button('dump current',fire_dump='runningSites.command')
        fb.button('stop current',fire_stop='runningSites.command')
        fb.button('load current',fire_load='runningSites.command')

        bc.borderContainer(region='center',background='whitesmoke')

    @public_method
    def daemonCommands(self,command=None,sitename=None):
        return getattr(self.site.register.gnrdaemon_proxy,'siteregister_%s' %command,None)(sitename)
        

    @public_method
    def runningSites(self):
        result = Bag()
        sites = self.site.register.gnrdaemon_proxy.siteRegisters()
        print sites
        for k, v in sites:
            result.setItem(k,None,**v)
        return result