#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
# Genro Web example app
# log as: mrossi password: reds
#

""" GnrDojo Hello World """
import os
from gnr.core.gnrbag import Bag, BagResolver
class GnrCustomWebPage(object):
# BEGIN main page definition
    def pageAuthTags(self, method=None, **kwargs):
        return 'user'
    
    def main(self, root, **kwargs):
        # the rootLayoutContainer method adds menubar of the site folder
        root=self.rootLayoutContainer(root)
        
    # BEGIN overall layout definition
        lc = root.layoutContainer(height='100%')
        titlepane = lc.contentPane(layoutAlign='top', _class='titlepane').span('Genro Rss Reader')
        main = lc.contentPane(layoutAlign='client')
        mainsplitter = main.splitContainer(height='100%', sizerWidth=5)
        treepane = mainsplitter.contentPane(sizeShare=18, _class='treepane')
        client = mainsplitter.contentPane(sizeShare=82)
        bottomline = lc.contentPane(layoutAlign='bottom', _class='bottomline')
    # END overall layout definition
    
    # BEGIN rss treepane content definition
        topicsTree = treepane.div(_class='treecontainer').tree(datasource='topics', gnrId ='topictree', nodelabel='title')
        # clientside tree's datasource is provided by rpc method configureUser.
        topicsTree.data(remote= 'configureUser')
        
        # defining two client functions as topicsTree's properties
            # setCurTopic sets the Data Bag with the feeds' topics path to the path 'newfeed.topic'
        topicsTree.func('setCurTopic', 
                        'treenode',
                        """
                        var datanode = genro.getDataNode(treenode) 
                            //returns the datanode connected to the selected treenode
                            
                        if (!datanode.hasAttr('url')){ //if datanode is not a feed node
                            genro.setData('newfeed.topic',
                                       datanode.getFullpath().slice(12))
                        }   //set the topics at the path 'newfeed.topic' of Data Bag
                        """)
                        
            # setCurFeed sets the Data Bag with the feeds' path, to the path 'currentfeed'
        topicsTree.func('setCurFeed', 
                        'treenode',
                        """
                        var datanode = genro.getDataNode(treenode)
                            //returns the datanode connected to the selected treenode
                            
                        if (datanode.getAttr('isFolder')==false){//if datanode is a feed node
                            genro.setData('currentFeed',datanode.getValue()) 
                            //set the feed's value at the path 'currentFeed' of Data Bag
                        }                              
                        """)
                        
        # subscribing these function to the tree's event onSelect
        topicsTree.subscribe(topicsTree, event='onSelect', func='*setCurTopic')
        topicsTree.subscribe(topicsTree, event='onSelect', func='*setCurFeed')
    # END rss treepane content definition
    
    # BEGIN subscription pane content definition
        # defining a table with two input forms and a button
        subtab = bottomline.table()
        row =subtab.tr()
        row.td('Topic:',_class='label')
        row.td().input(datasource ='newfeed.topic', 
                       _class='field', validate_notNull='Y',
                       validate_case='capitalize')
        row.td('Url:', _class='label')
        row.td().input(datasource ='newfeed.url', _class='urlfield')
        confirmbtn = row.td().button(caption='confirm')
        
        # defining the button's function for adding a feed
        
        confirmbtn.func('saveFeed','',"""
                    var params = {'topic':genro.getData('newfeed.topic'),
                                  'url':genro.getData('newfeed.url')} ;
                    
                    genro.rpc.remoteCall('saveFeed', params, null, 'POST');
                      
                        // it calls the server method rpc_saveFeed
                        
                    genro.getDataNode('topics').resetResolver()
                        // refresh the resolver connected to the tree
                """)
                
        # subscribing the funtion to the button's event onClick
        confirmbtn.subscribe(confirmbtn, event='onClick', func='*saveFeed')
             
     # END subscription pane on page content definition
     
     # BEGIN client pane on page content definition
        clientsplitter=client.splitContainer(height='100%',width='100%', sizerWidth=5, orientation='vertical')
        tablepane = clientsplitter.contentPane(sizeShare=30)
        
        # the widget bagFilteringTable gets its data from 'currentFeed'
        newstable = tablepane.bagFilteringTable(datasource='currentFeed', 
                                               alternateRows=True, multiple=True,
                                               _class='dojo', gnrId='newstable',columns='title,description,pubDate')
        
        newspane = clientsplitter.contentPane(sizeShare=70, _class='iframeCont')
        # iframe object definition
        newsframe = newspane.iframe(height='100%',width='100%', gnrId = 'newsframe',border='0px') 
        
        # this function set iframe's url
        newsframe.func('viewNews','newsid, event',"""
                                               url = genro.getData('currentFeed.rows.'+newsid+'.link')
                                               genro.dom.iFrameSetUrl(genro.newsframe, url,true);
                                               """)
        # subscribing viewNews() to the bagfilteringtable's event onSelectionDone
        newsframe.subscribe(newstable, event='onSelectionDone', func='*viewNews')
    # END client pane on page content definition
# END main page definition

#BEGIN rpc methods
    
    def authenticateUser(self, user, password):
        dbtable = 'rss.user'
        record = self.app.db.table(dbtable).record(pkey=user).output('bag') 
        if(record):
            return (record['password'] == password)


    def pageAuthTags(self,method=None,**kwargs):
        return "User"

    def rpc_configureUser(self):
        """
             get the user from object request, set its configuration
             into a Genro Bag as property.
        """
        user=self.user
        usereSelection = self.app.db.query('rss.feed',where='$user_id=:u', sqlparams={'u':user}).selection()
        userSelection.output('bag')
    
        topicView=Bag()
        # fill the bag topicView with the right data
        for i,fbag in enumerate(userfeeds.values()):
            topicView.addItem('%s.feed%i' % (fbag['topic'],i) ,
                               RssFeedResolver(feed=fbag['url']),
                              isFolder=False, title=fbag['name'], url= fbag['url'])
            # set RssFeedResolver as bag node value
        # return the bag topicView to the Data Bag on the client side
        return topicView
     
                                    
    def rpc_saveFeed(self, url, topic):
        """
             save new feed into user's configuration XML file.
        """
        url=url.replace('feed://','http://')
        feedBag = Bag()
        feedBag['user_id']=self.user
        feedBag['url']=url
        feedBag['topic']=topic
        f=Bag(url)['rss.channel']
        feedBag['name'] = f.getItem('title')
        lurl=url.split('.')
        if len(lurl)==3:
            feedBag['channel']=lurl[0][7:]
        else:
            feedBag['channel']=lurl[1]
        tbl = self.app.db.table('rss.feed')
        tbl.insertOrUpdate(feedBag)
        self.app.db.commit()
        return 'ok'
        
    def rpc_savenews(self, rows):
        b= Bag(rows)
        raise str(b)
        for elem in b.values():
            self.app.rpc_saveRecord(dbtable='rss.article', recordBag=elem)
    

        
#END rpc methods
   
# BEGIN RssFeedResolver class definition

# look at bag manual
class RssFeedResolver(BagResolver):
    classKwargs={'cacheTime':300,
                 'readOnly':False}
    classArgs=['feed']

    def load(self):
        feed= Bag(self.feed)['rss.channel']
        result= Bag()
        news=Bag()
        i=0
        for k,v in feed.items():
            if k=='item':
                i=i+1
                news['rows.r%i' %i]=v
        news.setItem('headers.title',None, label='Title')
        news.setItem('headers.author',None, label='Author')
        news.setItem('headers.description',None, label='Abstract')
        news.setItem('headers.pubDate',None, label='Date',dataType='D')
        
        return news
# END RssFeedResolver class definition

# ------------ Standard Rpc Call ------------


