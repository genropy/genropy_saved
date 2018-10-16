from gnr.web.gnrbaseclasses import BaseComponent
from gnr.core.gnrdecorator import public_method
from gnr.web.gnrwebstruct import struct_method

class BottomPlugins(BaseComponent):
    py_requires='gnrcomponents/doc_handler/doc_handler:DocHandler'
    documentation = False
    tickets = False

    def onMain_bottomplugin(self):
        if self.parent_page_id != self.root_page_id:
            return
        _gnrRoot = self.pageSource('_gnrRoot')
        #tblcode = self.maintable.replace('.','_')
        #if self.pbl_isDocWriter() or os.path.exists(self.de_documentPath(storeKey=tblcode,doctype='html')):
        if self.documentation or self.tickets:
            rootbc = _gnrRoot.value
            bottom = rootbc.contentPane(region='bottom',height='30%',
                                    splitter=True,closable='close',
                                    border_top='1px solid gray',
                                    overflow='hidden',
                                    background='white')
            bottom.contentPane(overflow='hidden').remote(self.bp_fillbottomplugins)
            rootbc.dataController("""if(rootbc.isRegionVisible('bottom')){
                    if(setting){
                        rootbc.showHideRegion('bottom',false);
                        this._snapshot_hidden = true;
                    }
                }
                if(this._snapshot_hidden && !setting){
                    delete this._snapshot_hidden;
                    rootbc.showHideRegion('bottom',true);
                }
            """,rootbc=rootbc.js_widget,subscribe_onPageSnapshot=True,bottom=bottom)
            if self.tickets:
                rootbc.dataController("""
                    if(!rootbc.isRegionVisible('bottom')){
                        rootbc.showHideRegion('bottom',true);
                    }
                    var that = this;
                    setTimeout(function(){
                            that.setRelativeData('gnr.bottomplugins.selectedPage','tickets');
                            that.fireEvent('gnr.bottomplugins.newticket',true);
                        },500);
                    """,rootbc=rootbc.js_widget,subscribe_genro_report_bug=True)

    @public_method
    def bp_fillbottomplugins(self,pane):
        sc = pane.stackContainer(datapath='gnr.bottomplugins',selectedPage='^.selectedPage')
        if self.documentation:
            sc.contentPane(title='!!Documentation',iconTitle='icnBottomDocumentation',overflow='hidden',pageName='docs').docFrameMulti().adaptToolbar()
        if self.tickets:
            ticketpane = sc.contentPane(title='!!Tickets',iconTitle='icnBottomTicket',overflow='hidden',pageName='tickets',datapath='tickets')
            tickets_view = ticketpane.ticketFrame(code='main')
            tickets_view.adaptToolbar()
            ticketpane.dataController("""ticket_form.form.newrecord();
                ticket_form.fireEvent('#FORM.showImagesPicker',true);
                """,fired='^gnr.bottomplugins.newticket',ticket_form=ticketpane.form)
            

    @struct_method
    def bp_adaptToolbar(self,frame):
        frame.top.bar.replaceSlots('#','5,parentStackButtons,#',gradient_to='#569EFF',
                                gradient_from='#3B4D64',gradient_deg=90,
                                toolbar=False,_class='iconbox_small',height='24px')