# -*- coding: UTF-8 -*-

# thpage.py
# Created by Francesco Porcari on 2011-05-05.
# Copyright (c) 2011 Softwell. All rights reserved.

from gnr.web.gnrwebstruct import struct_method


class GnrCustomWebPage(object):
    py_requires='gnrcomponents/doc_handler/doc_handler:DocHandler,gnrcomponents/ticket_handler/ticket_handler:TicketHandler'

    documentation = 'auto'

        

    def main(self,root,**kwargs):
        root.attributes.update(overflow='hidden')
        frame = root.framePane(datapath='main',selectedPage='^.selectedPage',margin='2px')
        frame.top.slotToolbar('*,stackButtons,*',gradient_from='#999',gradient_to='#666',height='20px')
        tc = frame.center.stackContainer()

        root.dataController("""var fm = genro.getParentGenro().framedIndexManager;
                                SET gnr.doc.main.pages = fm.callOnCurrentIframe('docHandler','getDocumentationPages');
                                var r = fm.callOnCurrentIframe('ticketHandler','getTicketInfo');
                                SET tickets_info.project_code = r.project_code;
                                SET tickets_info.package_identifier = r.package_identifier;
                                SET tickets_info.table_identifier = r.table_identifier;
                                SET tickets_info.pagename = r.pagename;
                                FIRE tickets.run;

                            """,
                            subscribe_onSelectedFrame=True,
                            _onStart=True)
        docpane = tc.contentPane(title='!!Documentation',xiconTitle='icnBottomDocumentation',
                            overflow='hidden',pageName='docs')
        docpane.docFrameMulti()
        ticketpane = tc.contentPane(title='!!Tickets',xiconTitle='icnBottomTicket',overflow='hidden',pageName='tickets',datapath='tickets')
        if self.db.package('uke'):
            ticketpane.ticketFrame(pagename='=tickets_info.pagename',project_code='=tickets_info.project_code',
                                        package_identifier='=tickets_info.package_identifier',
                                        table_identifier='=tickets_info.table_identifier')