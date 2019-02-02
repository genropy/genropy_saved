# -*- coding: utf-8 -*-

# thpage.py
# Created by Francesco Porcari on 2011-05-05.
# Copyright (c) 2011 Softwell. All rights reserved.

from builtins import object
from gnr.web.gnrwebstruct import struct_method


class GnrCustomWebPage(object):
    py_requires='ticket_handler/ticket_handler:TicketHandler'


    def main(self,root,**kwargs):
        root.attributes.update(overflow='hidden')
        frame = root.framePane(datapath='main',selectedPage='^.selectedPage',margin='2px')
        frame.top.slotToolbar('*,stackButtons,*',gradient_from='#999',gradient_to='#666',height='20px')
        tc = frame.center.stackContainer()
        
       #docpane = tc.contentPane(title='!!Documentation',xiconTitle='icnBottomDocumentation',
       #                        overflow='hidden',pageName='docs')
       #docpane.docFrameMulti()
        helpdesk = self.getPreference('helpdesk',pkg='adm')
        if helpdesk['client_reference']:
            frame.dataController("""
                                
                                var fm =genro.externalParentWindow.genro.framedIndexManager;
                                var linkedframe = fm.getCurrentIframe(fm.stackSourceNode.getRelativeData('selectedFrame'))
                                var linkedwindow = linkedframe.contentWindow;
                                if(!linkedwindow.genro){
                                    return;
                                }
                                var linkedgenro = linkedwindow.genro;

                                var project_code = linkedgenro.getData('gnr.project_code');
                                var package_identifier = project_code+'/'+linkedgenro.getData('gnr.package');

                                SET tickets_info.project_code = project_code;
                                SET tickets_info.package_identifier = package_identifier;
                                SET tickets_info.table_identifier = package_identifier+'/'+linkedgenro.getData('gnr.table');
                                SET tickets_info.pagename = linkedgenro.getData('gnr.pagename');
                                PUBLISH getTickets;
                            """,_onBuilt=True)

            ticketpane = tc.contentPane(title='!!Tickets',xiconTitle='icnBottomTicket',overflow='hidden',pageName='tickets',datapath='tickets')
            ticketpane.ticketFrame(pagename='=tickets_info.pagename',
                                        project_code='=tickets_info.project_code',
                                        package_identifier='=tickets_info.package_identifier',
                                        table_identifier='=tickets_info.table_identifier',
                                        client_reference=helpdesk['client_reference'],
                                        url=helpdesk['url'],
                                        user= helpdesk['user'],
                                        password= helpdesk['password'])