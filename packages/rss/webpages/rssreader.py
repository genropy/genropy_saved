#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#
#  untitled
#
#  Created by Giovanni Porcari on 2007-03-24.
#  Copyright (c) 2007 Softwell. All rights reserved.
#

""" RSS READER """
from gnr.core.gnrbag import Bag

class GnrCustomWebPage(object):
    maintable='rss.feed'
    css_require='rssreader'
    
    def pageAuthTags(self, **kwargs):
        return 'user'
        
    def main(self, root, **kwargs):
        layout = root.borderContainer(design="sidebar")
        self.left(layout.borderContainer(region='left', width="30%", splitter=True,
                                          _class='fakeclass',datapath='feed'))
        self.top(layout.contentPane(region='top',height='30%', splitter=True,_class='fakeclass'))
        center = layout.stackContainer(region='center',_class='fakeclass',selectedPage='^rss.page') 
        center.contentPane(pageName='loading').div('...Loading...')  
        center.contentPane(pageName='loaded').iframe(height='100%',width='100%',
                                                    delay=2000,border='0',    
                                                    onUpdating='genro.setData("rss.page","loading");',
                                                    onLoad='genro.setData("rss.page","loaded");',
                                                    src='^rss.link')           
        
    def left(self,bc):
        self.feedform(bc.contentPane(region='top',_class='fakeclass'))
        center = bc.contentPane(region='center',_class='fakeclass')
        center.tree(storepath='.tree',labelAttribute='caption',selected_k_id='.curr.pkey',   
                    selected_k_url='.curr.url',_fired='^.refreshTree', inspect='shift')
        center.dataRpc('.tree','getFeeds',_fired='^.refresh',_onResult='FIRE .refreshTree',_onStart=True)
        center.dataRpc('rss.rows','getItems',url='^.curr.url',_if='url',_else="null")
    
    def feedform(self,pane):
        fb = pane.formbuilder(cols=2,border_spacing='4px',datapath='.record',formId='rss', 
                            controllerPath='form',pkeyPath='feed.curr.pkey',
                            width='90%',dbtable='rss.feed')
        #fb.textbox(value='^.topic',lbl='!!Topic',width='100%')
        #fb.textbox(value='^.title',lbl='!!Title',width='100%')
        #fb.textbox(value='^.url',lbl='!!Address',colspan='2',width='100%')         
        fb.field('topic',autospan=1)   
        fb.field('title',autospan=1)
        fb.field('url',autospan=2)
        
        fb.button('!!Save',action="genro.formById('rss').save();",
                    disabled='==!_valid',_valid='^form.valid')
        fb.button('!!New',action="FIRE feed.curr.pkey='*newrecord*';")   
         
        # == ritorna un espressione javascript    
        pane.dataController("""       
                            genro.formById('rss').load({destPkey:destPkey});""",
                            destPkey='^.curr.pkey',_onStart=True)           
         
        pane.dataRpc('.savedId','saveFeed',record='=.record',
                    _onResult="""       
                                genro.formById('rss').saved();
                                FIRE .refresh;""",nodeId='rss_saver')  
        pane.dataRecord('.record','rss.feed',pkey='=.curr.pkey',nodeId='rss_loader',
                        _onResult="genro.formById('rss').loaded()")
                          
    def rpc_saveFeed(self,record=None,**kwargs):
        tblfeed = self.db.table(self.maintable)
        if not record['id']:
            record['username'] = self.user
            tblfeed.insert(record)
        else:
            tblfeed.update(record)
        self.db.commit()
        return record['id']
    
    def rpc_getFeeds(self):
        results = self.db.table(self.maintable).getFeeds(user = self.user) 
        return  results

    def rpc_getItems(self,url=None,**kwargs):
        rss=Bag(url)['rss.channel'].digest('#v') 
        rows = Bag()   
        for i,item in enumerate(rss):
            if isinstance(item,Bag):
                rows.setItem('n_%i' %i,None,title=item['title'],link=item['link'],description=item['description'])
        return  rows  
                                                 
                                               
    def item_struct(self):
        struct = self.newGridStruct()
        r = struct.view().rows()
        r.cell('title', name='!!Title', width='20em',classes='titleCell')       
        r.cell('description', name='!!Description', width='50em',classes='descCell')  
        return struct
        
        
    def top(self,pane):
        pane.includedView(storepath='rss.rows',
                          nodeId='rssItemsGrid',autoWidth=True,        
                          selected_link='rss.link',
                          struct=self.item_struct())

        
        
            
                
            
