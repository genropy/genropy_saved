# -*- coding: UTF-8 -*-

# test_iframe.py
# Created by Francesco Porcari on 2011-02-14.
# Copyright (c) 2011 Softwell. All rights reserved.

"test_iframe"

from gnr.web.gnrwebstruct import struct_method

class GnrCustomWebPage(object):
    
    def windowTitle(self):
        return 'test_iframe'
        
    def main(self,pane,**kwargs):
        """First test description"""
        sc = pane.tabContainer(selectedPage='^currentPage',nodeId='maintab')
        frame = sc.framepane(frameCode='test',datapath='test',pageName='selector',title='aaa')
        top = frame.top.slotBar(slots='foo')
        fb =top.foo.formbuilder()
        fb.dbselect(value='^.prov',dbtable='glbl.provincia',lbl='Provincia')
        fb.dataController("SET currentPage=pageName;genro.publish({'topic':'load','iframe':'*','form':'baseform'},{destPkey:pkey});",
                           pkey="^.prov",pageName='test_iframe_inside')
        #rpc = fb.dataRpc('dummy','setInFrame',prov='^.prov',framePageId='=frame.test1.page_id')
        #rpc.addCallback('SET currentPage="test_iframe_inside";')
        sc.createFrameTab(pageName='test_iframe_inside',title='bbb')
        
    #def rpc_setInFrame(self,prov=None,framePageId=None,**kwargs):
    #    self.setInClientData('pkey', value=prov, page_id=framePageId,fired=False)
        
    @struct_method
    def createFrameTab(self,sc,pageName='',**kwargs):
        pane = sc.contentPane(pageName=pageName,overflow='hidden',**kwargs).contentPane(_lazyBuild=True,overflow='hidden')
        #pane.dataFormula("myurl", "url",url='http://127.0.0.1:8083/test15/html/%s' %pageName,_onStart=1000)
        pane.iframe(height='100%',width='100%',border='0',nodeId=pageName,src=pageName,
                    onCreated='console.log("created");')