#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#
#  Migration
#
#  Created by Francesco Porcari on 2007-03-24.
#  Copyright (c) 2007 Softwell. All rights reserved.
#
import os
import gzip
from StringIO import StringIO
import pickle

from gnr.core.gnrdecorator import public_method
from gnr.core.gnrbag import Bag

class GnrCustomWebPage(object):
    py_requires="""public:Public,
                   gnrcomponents/framegrid:FrameGrid"""
    pageOptions={'openMenu':False,'enableZoom':False}
    auth_main = 'admin'

    def windowTitle(self):
        return '!!Startup data'

    def main(self, root, **kwargs):
        bc = root.rootBorderContainer(title='Startup data',datapath='main',design='sidebar')
        self.packageData(bc,region='center')
    

    def packageData(self,pane,pkg=None,**kwargs):
        bc = pane.borderContainer(**kwargs)
        top = bc.contentPane(region='top')
        fb = top.formbuilder(cols=6,border_spacing='3px')
        fb.filteringSelect(value='^.current_package',lbl='Package',values=','.join(self.application.packages.keys()))
        fb.button('!!Build Startup Data',action="""genro.mainGenroWindow.genro.publish('open_batch');
                                                    var that = this;
                                                    genro.serverCall('_package.'+pkg+'.createStartupData',null,function(){
                                                        that.fireEvent('.reloadPreview')
                                                    });
                                                    """,pkg='=.current_package')
        fb.button('!!Load Startup Data',action="""genro.mainGenroWindow.genro.publish('open_batch');
                                                    genro.serverCall('_package.'+pkg+'.loadStartupData',{empty_before:empty_before},function(){});
                                                    """ ,pkg='=.current_package',empty_before=True,
                                                    ask=dict(title='Delete table contents',fields=[dict(name='empty_before',
                                                                                                            label='Delete tables before import',
                                                                                                            wdg='checkbox')]))
        fb.button('!!Refresh preview',fire='.reloadPreview')
        center = bc.borderContainer(region='center',_class='pbl_roundedGroup',margin='2px')
        center.dataRpc('.startup_tables',self.getStartupTables,pkg='^.current_package',_fired='^.reloadPreview')
        center.contentPane(region='top',_class='pbl_roundedGroupLabel').div('Startup tables')
        center.contentPane(region='center',overflow='hidden').quickGrid('^.startup_tables')

    @public_method
    def getStartupTables(self,pkg=None):
        bagpath = os.path.join(self.db.application.packages[pkg].packageFolder,'startup_data')
        data = None
        if not os.path.isfile('%s.pik' %bagpath):
            if not os.path.exists('%s.gz' %bagpath):

                return
            with gzip.open('%s.gz' %bagpath,'rb') as gzfile:
                pk = StringIO(gzfile.read())
                data = pickle.load(pk)
        else:
            data = Bag('%s.pik' %bagpath)
        result = Bag()
        for i,t in enumerate(data['tables']):
            row = Bag()
            row['table'] = t
            row['count'] = len(data[t])
            result['r_%s' %i] = row
        return result
