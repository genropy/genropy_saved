from gnr.web.gnrbaseclasses import BaseComponent
from gnr.core.gnrdecorator import public_method
from gnr.web.gnrwebstruct import struct_method

class BottomPlugins(BaseComponent):
    py_requires='gnrcomponents/doc_handler/doc_handler:DocHandler,gnrcomponents/ticket_handler/ticket_handler:TicketHandler'
    documentation = False
    tickets = False

    def onMain_bottomplugin(self):
        _gnrRoot = self.pageSource('_gnrRoot')
        #tblcode = self.maintable.replace('.','_')
        #if self.pbl_isDocWriter() or os.path.exists(self.de_documentPath(storeKey=tblcode,doctype='html')):
        if self.documentation or self.tickets:
            bottom = _gnrRoot.value.contentPane(region='bottom',height='30%',
                                    splitter=True,drawer='close',
                                    border_top='1px solid gray',
                                    overflow='hidden',
                                    background='white')
            bottom.contentPane(overflow='hidden').remote(self.bp_fillbottomplugins)

    @public_method
    def bp_fillbottomplugins(self,pane):
        sc = pane.stackContainer(datapath='pbl_bottom')
        if self.documentation:
            sc.contentPane(title='!!Documentation',iconTitle='icnBottomDocumentation',overflow='hidden').docFrameMulti().adaptToolbar()
        if self.tickets:
            sc.contentPane(title='!!Tickets',iconTitle='icnBottomTicket',overflow='hidden').ticketFrame(code='main').adaptToolbar()

    @struct_method
    def bp_adaptToolbar(self,frame):
        frame.top.bar.replaceSlots('#','5,parentStackButtons,#',gradient_to='#569EFF',
                                gradient_from='#3B4D64',gradient_deg=90,
                                toolbar=False,_class='iconbox_small',height='24px')