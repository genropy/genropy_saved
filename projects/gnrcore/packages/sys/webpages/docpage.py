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
        frame = root.framePane(datapath='main',selectedPage='^.selectedPage',margin='2px')
        frame.top.slotToolbar('*,stackButtons,*',gradient_from='#999',gradient_to='#666',height='20px')
        tc = frame.center.stackContainer()

        root.dataController("""var fm = genro.getParentGenro().framedIndexManager;
                                SET gnr.doc.main.pages = fm.callOnCurrentIframe('docHandler','getDocumentationPages');
                                SET tickets.folders = fm.callOnCurrentIframe('ticketHandler','getTicketFolders');

                            """,
                            subscribe_onSelectedFrame=True,
                            _onStart=True)
        docpane = tc.contentPane(title='!!Documentation',xiconTitle='icnBottomDocumentation',
                            overflow='hidden',pageName='docs')
        docpane.docFrameMulti()
        ticketpane = tc.contentPane(title='!!Tickets',xiconTitle='icnBottomTicket',overflow='hidden',pageName='tickets',datapath='tickets')
        ticketpane.ticketFrame(code='main',folders='^tickets.folders')