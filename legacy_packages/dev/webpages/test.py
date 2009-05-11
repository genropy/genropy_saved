#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
""" GnrDojo Hello World """

from gnr.web.gnrwebcore import GnrWebPage, GnrWebClientError
import datetime, subprocess
from gnr.core.gnrbag import Bag, DirectoryResolver

#-------  configure: customize this configuration ------
class GnrCustomWebPage(object):
    def main(self, root, **kwargs):
        root = self.rootLayoutContainer(root,padding='2px')
        root.h1('prova')
        root.div('instance customized page attributes:%s' %self.credits)
        root.div('instance customized page method:%s' %self.myCustomPageMethod('life'))
        
        root.div('instance customized application attributes:%i' %self.application.maxConnections)
        root.div('instance customized application method:%s' %self.application.myCustomAppMethod('life'))
        
        root.div('package doThis: %s' %self.package.doThis('unleash hell'))
        for t in self.package.sqlPkg.tables.values():
            root.div('A table doThis: %s' % t.doThis('common stuff'))
        root.div('page authTags:%s' %self.pageAuthTags(method='main'))
    
        
        t=root.table(gnrId='btnTable')
        tr=t.tr()
        tr.td().button(caption='test action:command',action="alert('test command')", connect_onmouseover="alert('onmouseover')")
        tr.td().button(caption='test action:function',action="function(evt){alert('test function: evt '+evt.target)}")
        tr.td().button(caption='test action:server',action="genro.serverCall('servertest',{'pippo':45,'pluto':'ooo'})")
        tr.td().button(caption='test action:server+callback',action="genro.serverCall('servertest',{'pippo':45,'pluto':'ooo'},'alert(arguments[0])')")
        tr=t.tr()
        #tr.td().button(caption='test of connect',connect_onclick='alert("clicked")',connect_onmouseover='alert("mouseover")')
        tr.td().button(caption='alert no btn',action="""genro.dlg.alert('Hai appena attivato il dispositivo k')""")
        tr.td().button(caption='alert',action="""genro.dlg.alert('Vuoi davvero fare pux?',{'Annulla':'alert("come non detto")','Forse':'alert("deciditi")','Conferma':'alert("ecco fatto")'})""")
        
        tr.td().button(caption='confirm')
        tr.td().button(caption='request')

    def rpc_servertest(self,**kwargs):
        self.gnotify('servertest',str(kwargs))
        return 'here is the result:'+str(kwargs)
 
    def pageAuthTags(self, method=None, **kwargs):
        if method=='main':
            return "boss; developer AND softwell NOT junior; pippolone"

#---- rpc index call -----
def index(req, **kwargs):
    return GnrWebPage(req, GnrCustomWebPage, __file__, **kwargs).index()
