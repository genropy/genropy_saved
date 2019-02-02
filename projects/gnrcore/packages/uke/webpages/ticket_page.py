#!/usr/bin/env python
# encoding: utf-8
"""
order_page.py

Created by Saverio Porcari on 2012-06-21.
Copyright (c) 2012 __MyCompanyName__. All rights reserved.
"""

from builtins import object
from gnr.core.gnrdecorator import public_method
from gnr.core.gnrbag import Bag


class GnrCustomWebPage(object):
    maintable='uke.ticket'
    py_requires='public:Public,public:TableHandlerMain'
    pageOptions=dict(openMenu=False)

    def onMain_ticket_manager(self):
        page = self.pageSource()
        page.dataController("""
            SET uke.contest.pagename = pagename; 
            SET uke.contest.user = user; 
            SET uke.contest.package = pkg; 
            SET uke.contest.project = project; 
            SET uke.contest.maintable = maintable; 
            SET uke.contest.maintable_project = maintable; 
            SET uke.defaults.package_identifier = project+'/'+pkg;
            if(maintable){
                SET uke.defaults.table_identifier = [maintable_project].concat(maintable.split('.')).join('/');
            }

            """,subscribe_onOpenTicketManager=True)

    def th_options(self):
        return dict(viewResource='TicketManagerView',
                    formResource='TicketManagerForm',public=False,
                    extendedQuery=False,virtualStore=False)