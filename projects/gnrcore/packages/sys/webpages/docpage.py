# -*- coding: UTF-8 -*-

# thpage.py
# Created by Francesco Porcari on 2011-05-05.
# Copyright (c) 2011 Softwell. All rights reserved.

from gnr.web.gnrwebstruct import struct_method


class GnrCustomWebPage(object):
    py_requires='gnrcomponents/doc_handler/doc_handler:DocHandler,gnrcomponents/ticket_handler/ticket_handler:TicketHandler'

    documentation = 'auto'

   # @classmethod
   # def getMainPackage(cls,request_args=None,request_kwargs=None):
   #     return request_kwargs.get('th_from_package') or request_args[0]
        

    def main(self,root,**kwargs):
        root.attributes.update(overflow='hidden')
        tc = root.tabContainer(datapath='main',selectedPage='^.selectedPage',margin='2px')


        root.dataController("""var result = genro.getParentGenro().framedIndexManager.getCurrentDocumentation();
                                SET gnr.doc.main.pages = result.documentation;
                                SET tickets.folders = result.tickets;

                            """,
                            subscribe_onSelectedFrame=True,
                            _onStart=True)
        docpane = tc.contentPane(title='!!Documentation',iconTitle='icnBottomDocumentation',overflow='hidden',pageName='docs')
        docpane.docFrameMulti()
    
        ticketpane = tc.contentPane(title='!!Tickets',iconTitle='icnBottomTicket',overflow='hidden',pageName='tickets',datapath='tickets')
        ticketpane.ticketFrame(code='main',folders='^tickets.folders')


    @struct_method
    def bp_adaptToolbar(self,frame):
        frame.top.bar.replaceSlots('#','5,parentStackButtons,#',height='20px')