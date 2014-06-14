from gnr.web.gnrwebpage import BaseComponent
from gnr.web.gnrwebstruct import struct_method
from gnr.core.gnrdecorator import public_method



class TicketHandler(BaseComponent):
    py_requires ='gnrcomponents/framegrid:FrameGrid,gnrcomponents/formhandler:FormHandler'
    ticket_path = ''
    @struct_method
    def tk_ticketFrame(self,pane,code=None,**kwargs):
        view = pane.frameGrid(frameCode='V_ticketframe_%s' %code,struct=self.tk_struct_ticket,
                                    gridEditor=False,
                                    autoToolbar=False,
                                    datapath='.view',**kwargs)
        view.top.slotToolbar('*,delrow,addrow,5',gradient_from='#030F1F',gradient_to='#3B4D64')
        view.grid.fsStore(childname='store',folders=self.tk_ticketFolder(),_onBuilt=True)
        form = view.grid.linkedForm(frameCode='F_ticketframe_%s' %code,
                                 datapath='.form',loadEvent='onRowDblClick',
                                 dialog_height='450px',dialog_width='620px',
                                 dialog_title='Ticket',
                                 handlerType='dialog',
                                 childname='form',attachTo=pane,
                                 store='document')
        self.tk_ticket_form(form)
        return view

    def tk_ticket_form(self,form):
        form.top.slotToolbar('2,navigation,*,delete,add,save,semaphore,locker,2')
        fb = form.record.formbuilder(cols=1,border_spacing='3px')
        fb.textbox(value='^.name',lbl='Code')
        fb.textbox(value='^.description',lbl='Description')
        fb.dateTextBox(value='^.date',lbl='Date')

    def tk_struct_ticket(self,struct):
        r = struct.view().rows()
        r.cell('path',hidden=True)
        r.cell('name',width='10em',name='!!Name')
        r.cell('ticket_type',width='10em',name='!!Type')
        r.cell('description',width='20em',name='!!Description')
        r.cell('date',dtype='D',width='5em',name='!!Date')
        r.cell('user',width='5em',name='User')
        r.cell('status',width='10em',name='!!Description')

    def tk_ticketFolder(self):
        if self.ticket_path:
            return self.ticket_path
        elif self.maintable:
            tbllist = self.maintable.split('.')
            pkg = self.package.name
            tblpkg = tbllist[0]
            if tblpkg==pkg:
                return self.site.getStaticPath('pkg:%s' %pkg,'tickets',
                    'tables',tbllist[1],autocreate=-1)
            else:
                return self.site.getStaticPath('pkg:%s' %pkg,'tickets',
                    'tables','_packages',tbllist[0],tbllist[1],autocreate=-1)


