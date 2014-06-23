from gnr.web.gnrwebpage import BaseComponent
from gnr.web.gnrwebstruct import struct_method
from gnr.core.gnrdecorator import public_method
from gnr.core.gnrstring import slugify
from gnr.core.gnrbag import Bag
from datetime import datetime
import os



class TicketHandler(BaseComponent):
    py_requires ='gnrcomponents/framegrid:FrameGrid,gnrcomponents/formhandler:FormHandler'
    ticket_path = ''
    @struct_method
    def tk_ticketFrame(self,pane,code=None,**kwargs):
        view = pane.frameGrid(frameCode='V_ticketframe_%s' %code,struct=self.tk_struct_ticket,
                                    gridEditor=False,
                                    autoToolbar=False,
                                    datapath='.view',grid_rowStatusColumn=True,**kwargs)
        view.top.slotToolbar('*,delrow,addrow,viewlocker,5',gradient_from='#030F1F',gradient_to='#3B4D64')
        fstore = view.grid.fsStore(childname='store',
                                    folders=self.tk_ticketFolder(allFolders=True),
                                    applymethod=self.tk_checkFilePermission)
        view.dataController("fstore.store.loadData();fstore.store.setLocked(true)",fstore=fstore,_onBuilt=True)
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
        form.store.handler('save',rpcmethod=self.tk_saveTicket)
        form.store.handler('load',default_ticket_type='B',default_status='N',rpcmethod='tk_loadTicket')
        form.top.slotToolbar('2,navigation,*,delete,add,save,semaphore,locker,2')
        bc = form.center.borderContainer(datapath='.record')
        fb = bc.contentPane(region='top',padding='10px').formbuilder(cols=3,border_spacing='3px',
                            colswidth='auto',tdl_padding_left='4px',fld_width='100%')
        fb.filteringSelect(value='^.ticket_type',lbl='Type',
                            values='B:Bug,C:Cosmetic,F:Feature Request',
                            validate_notnull=True)
        fb.textbox(value='^.title',lbl='Title',validate_notnull=True,
                    validate_remote=self.tk_validate_title,
                    validate_ticket_type = '^.ticket_type',
                    validate_mainfolder='^.mainfolder',
                    validate_ticket_id='=.__ticket_id',
                    colspan=2)
        fb.filteringSelect(value='^.status',lbl='status',validate_notnull=True,
                        values='N:New,P:In progress,S:Solved')
        fb.textbox(value='^.assigned_to',lbl='Assigned to')
        tbllist = self.maintable.split('.')
        pkg = self.package.name
        tblpkg = tbllist[0]
        if pkg!=tblpkg and self.isDeveloper():
            fb.checkbox('^.mainfolder',label='In original package')
        bc.roundedGroupFrame(title='Description',region='center').simpleTextArea(value='^.description',editor=True)


    def tk_struct_ticket(self,struct):
        r = struct.view().rows()
        r.cell('title',width='20em',name='!!Title')
        r.cell('ticket_type',width='10em',name='!!Type',values='B:Bug,C:Cosmetic,F:Feature Request')
        r.cell('description',width='30em',name='!!Description')
        r.cell('date',dtype='D',width='5em',name='!!Date')
        r.cell('created_by',width='5em',name='Created by')
        r.cell('assigned_to',width='5em',name='Assigned to')
        r.cell('status',width='10em',name='!!Status',values='N:New,P:In progress,S:Solved')

    @public_method
    def tk_validate_title(self,value,ticket_type=None,mainfolder=None,ticked_id=None,**kwargs):
        if not ticket_type:
            return
        newpath = self.tk_getTicketPath(value,ticket_type,mainfolder)
        if os.path.exists(newpath):
            r = Bag(newpath)
            if r['__ticket_id'] == ticked_id:
                return True
            else:
                return dict(errorcode='existing_another_file')
        return True

    @public_method
    def tk_loadTicket(self,path=None,**kwargs):
        resultAttr = dict()
        result = Bag()
        content = Bag(path)
        if content['created_by'] != self.user \
           and not ('superadmin' in self.userTags or '_DEV_' in self.userTags):
            resultAttr['_protect_write'] = True
        result.setItem('content',content,resultAttr)
        return result


    def tk_ticketFolder(self,useMainFolder=False,allFolders=None):
        if self.ticket_path:
            return self.ticket_path
        elif self.maintable:
            tbllist = self.maintable.split('.')
            pkg = self.package.name
            tblpkg = tbllist[0]
            mainpath = self.site.getStaticPath('pkg:%s' %tblpkg,'tickets','tables',tbllist[1])
            if tblpkg==pkg or useMainFolder:
                return mainpath
            custompath = self.site.getStaticPath('pkg:%s' %pkg,'tickets',
                    'tables','_packages',tbllist[0],tbllist[1])
            if allFolders:
                return ','.join([custompath,mainpath])
            return custompath

    def tk_getTicketPath(self,title,ticket_type,useMainFolder):
        return os.path.join(self.tk_ticketFolder(useMainFolder=useMainFolder),'%s.xml' %slugify('%s_%s' %(ticket_type,title)).replace('-','_'))

    @public_method
    def tk_saveTicket(self,path=None,data=None,**kwargs):
        title = data['title']
        ticket_type = data['ticket_type']
        removing_path = None
        newpath = self.tk_getTicketPath(title,ticket_type,data['mainfolder'])
        ts = datetime.now()
        data['__mod_ts'] = ts
        if path == '*newrecord*':
            path = newpath
            data['created_by'] = self.user
            data['date'] = self.workdate
            data['__ticket_id'] = self.getUuid()
            data['__ins_ts'] = ts
        elif path!=newpath:
            removing_path = path
            path = newpath
            title = data['title']
        destdir = os.path.dirname(path)
        if not os.path.exists(destdir):
            os.makedirs(destdir)
        data.toXml(filename=path)
        if removing_path:
            os.remove(removing_path)
        return dict(path=path)

    @public_method
    def tk_checkFilePermission(self,filesbag,**kwargs):
        if 'superadmin' in self.userTags or '_DEV_' in self.userTags:
            return 
        for n in filesbag:
            if n.attr['created_by']!=self.user:
                n.attr['_is_readonly_row'] = True


