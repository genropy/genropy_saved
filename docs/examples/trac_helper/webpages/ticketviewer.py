#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
# Genro Web example app
# log as: mrossi password: reds
#

""" GnrDojo Hello World """
import os
from gnr.web.gnrwebcore import GnrWebPage
from gnr.core.gnrbag import Bag, BagResolver
# --------------------------- GnrWebPage subclass ---------------------------
class GnrCustomWebPage(object):
# BEGIN main page definition
    def main(self, root, **kwargs):
        # the rootLayoutContainer method adds menubar of the site folder
        root=self.rootLayoutContainer(root)
        sc = root.splitContainer(height='100%',sizerWidth=5 )
        
    # BEGIN left
        leftPane = sc.contentPane(sizeShare=10)
        dctable =  leftPane.bagFilteringTable(datasource='data_changes', 
                                        alternateRows=True, multiple=True,
                                        _class='dojo', gnrId='ticket_change',columns='date')
        dctable.data(remote='loadTable')
        
        
        
    #main
    
        mainPane = sc.contentPane(sizeShare=90).splitContainer(height='100%',sizerWidth=5 ,orientation='vertical')
        ticketPane = mainPane.contentPane(sizeShare=50)
        ticketTable= ticketPane.bagFilteringTable(datasource='ticket', 
                                        alternateRows=True, multiple=True,
                                        _class='dojo', gnrId='ticket_change',columns='id,reporter,summary,description')
                                        
        ticketTable.func('viewTicket','dcId',"""
                        var params = {'date': genro.getData('data_changes.rows.'+dcId+'.'+'date')}
                        var ticketbag = genro.rpc.remoteCall('getTickets', params, null, 'GET');
                        genro.setData('ticket',ticketbag)
                        """)
        ticketTable.subscribe(dctable, event='onSelectionDone', func='*viewTicket')
       
       
        changeTable = mainPane.contentPane(sizeShare=50).bagFilteringTable(datasource='change', 
                                      alternateRows=True, multiple=True,
                                      _class='dojo', gnrId='ticket_change',columns='author,oldvalue,newvalue')
                                      
        changeTable.func('viewChanges','dcId',"""
                                    
                                        var params = {'ticketId': genro.getData('ticket.rows.'+dcId+'.'+'id')}
                                        var ticketbag = genro.rpc.remoteCall('getChanges', params, null, 'GET');
                                        genro.setData('change',ticketbag)
                                        """)
                                        
        changeTable.subscribe(ticketTable, event='onSelectionDone', func='*viewChanges')
        
    # END client pane on page content definition
    
    # ------------ Custom Rpc Calls ------------
    def rpc_loadTable(self):
        query = self.app.db.query('trac.ticket_change',columns="to_char(to_timestamp($time),'YYYY/MM/DD') as date", distinct=True)
        sel = query.selection()
        return sel.output('bag')
    
    def rpc_getTickets(self,date=None):
        query = self.app.db.query('trac.ticket', 
                                  columns="*", 
                                  where=" to_char(to_timestamp(@changes.time),'YYYY/MM/DD')= :datechange", 
                                  sqlparams={'datechange':date})
        sel = query.selection()
        return sel.output('bag')
        
    def rpc_getChanges(self,ticketId=None):
        query = self.app.db.query('trac.ticket_change', 
                                  columns="*", 
                                  where=" $ticket = :tId", 
                                  sqlparams={'tId':ticketId})
        sel = query.selection()
        return sel.output('bag')
        

# ------------ Standard Rpc Call ------------
def index(req, **kwargs):
    return GnrWebPage(req, GnrCustomWebPage, __file__, **kwargs).index()


