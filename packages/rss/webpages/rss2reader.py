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
    css_requires='rssreader'
    py_requires='public:RecordHandler'#we need to pass the name of components
    
    
    def pageAuthTags(self, **kwargs):
        return 'user'
        
    def main(self, root, **kwargs):
        layout = root.borderContainer(design="sidebar")
        self.left(layout.borderContainer(region='left', width="30%", splitter=True,datapath='left'))
        self.top(layout.contentPane(region='top',height='30%', splitter=True,_class='fakeclass'))
        center = layout.stackContainer(region='center',_class='fakeclass',selectedPage='^rss.page') 
        center.contentPane(pageName='loading').div('Browser',_class='browser')  
        center.contentPane(pageName='loaded').iframe(height='100%',width='100%',
                                                    delay=2000,border='0',    
                                                    onUpdating='genro.setData("rss.page","loading");',
                                                    onLoad='genro.setData("rss.page","loaded");',
                                                    src='^rss.link')
    def top(self,pane):
        pane.includedView(storepath='rss.rows',
                          nodeId='rssItemsGrid',autoWidth=False,
                          selected_link='rss.link',
                          struct=self.item_struct())
          
    def left(self,bc):
        pane=bc.contentPane(region='top')
        pane.div('Feed Reader',_class='title')
        buttons = pane.contentPane(_class='pad5')
        buttons.button('!!New Topic',action="FIRE newTopic")
        buttons.button('!!New Feed',action="FIRE newFeed")
        pane.div('Feeds:',_class='title')
        self.recordDialog('rss.topic', firedPkey='^newTopic',width='260px',height='100px',
                            formCb=self.topicform)
        self.recordDialog('rss.feed', firedPkey='^newFeed',width='260px',height='200px',
                            formCb=self.feedform,onSaved='FIRE .refreshTree',default_username=self.user)
        center = bc.contentPane(region='center',_class='fakeclass')
        center.tree(storepath='.tree',labelAttribute='caption',_fired='^.refreshTree',inspect='shift',
                    selected_k_id='.curr.pkey', selected_k_url='.curr.url',_class='pad5')
        center.dataRpc('.tree','getFeeds',_fired='^.refresh',_onResult='FIRE .refreshTree',_onStart=True)
        center.dataRpc('rss.rows','getItems',url='^.curr.url',_if='url',_else="null")

    def topicform(self,pane,**kwargs):
        fb = pane.formbuilder(cols=1,border_spacing='4px')
        fb.field('title',autospan=1)
        fb.field('description',autospan=1)

    def feedform(self,pane,**kwargs):
        fb = pane.formbuilder(cols=1,border_spacing='4px')
        fb.field('title',autospan=1)
        fb.field('description',autospan=1)
        fb.field('url',autospan=1)
        fb.field('topic',autospan=1,hasDownArrow=True)

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
        r.cell('description', name='!!Description', width='auto',classes='descCell')  
        return struct