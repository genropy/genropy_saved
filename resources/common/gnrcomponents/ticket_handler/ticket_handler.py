from gnr.web.gnrwebpage import BaseComponent
from gnr.web.gnrwebstruct import struct_method
from gnr.core.gnrdecorator import public_method,extract_kwargs
from gnr.core.gnrstring import slugify
from gnr.core.gnrbag import Bag
from datetime import datetime
import os
import shutil



class TicketHandler(BaseComponent):
    py_requires ='gnrcomponents/framegrid:FrameGrid,gnrcomponents/formhandler:FormHandler,gnrcomponents/filepicker:FilePicker'
    ticket_path = ''
    @struct_method
    def tk_ticketFrame(self,pane,code=None,**kwargs):
        view = pane.frameGrid(frameCode='V_ticketframe_%s' %code,struct=self.tk_struct_ticket,
                                    gridEditor=False,
                                    autoToolbar=False,
                                    datapath='.view',grid_rowStatusColumn=True,**kwargs)
        view.top.slotToolbar('*,delrow,addrow,viewlocker,5',gradient_from='#030F1F',gradient_to='#3B4D64')
        folders = self.tk_ticketFolder(allFolders=True)
        fstore = view.grid.fsStore(childname='store',
                                    folders=folders,
                                    include='ticket.xml',
                                    applymethod=self.tk_checkFilePermission,
                                    deletemethod=self.tk_deleteTicketRows)
        view.dataController("fstore.store.loadData();fstore.store.setLocked(true)",fstore=fstore,_onBuilt=True)
        form = view.grid.linkedForm(frameCode='F_ticketframe_%s' %code,
                                 datapath='.form',loadEvent='onRowDblClick',
                                 dialog_height='450px',dialog_width='620px',
                                 dialog_title='Ticket',
                                 handlerType='dialog',
                                 childname='form',attachTo=pane,
                                 store='document')
        self.tk_ticket_form(form,folders=folders)
        return view

    def tk_ticket_form(self,form,folders=None):
        form.store.handler('save',rpcmethod=self.tk_saveTicket)
        form.store.handler('load',default_ticket_type='B',default_status='N',rpcmethod='tk_loadTicket')
        form.top.slotToolbar('2,navigation,*,delete,add,save,semaphore,locker,2')
        bc = form.center.borderContainer()
        fb = bc.contentPane(region='top',padding='10px',datapath='.record').formbuilder(cols=3,border_spacing='3px',
                            colswidth='auto',tdl_padding_left='4px',fld_width='100%')
        fb.filteringSelect(value='^.ticket_type',lbl='Type',
                            values='B:Bug,C:Cosmetic,F:Feature Request',
                            validate_notnull=True)
        fb.textbox(value='^.title',lbl='Title',validate_notnull=True,colspan=2)
        fb.filteringSelect(value='^.status',lbl='status',validate_notnull=True,
                        values='N:New,P:In progress,S:Solved')
        fb.textbox(value='^.assigned_to',lbl='Assigned to')
        tbllist = self.maintable.split('.')
        pkg = self.package.name
        tblpkg = tbllist[0]
        if pkg!=tblpkg and self.isDeveloper():
            fb.checkbox('^.mainfolder',label='In original package')
        center = bc.roundedGroupFrame(title='Description',region='center')
        center.simpleTextArea(value='^.record.description',editor=True)
        bar = center.top.bar.replaceSlots('#','#,imgPick')
        customfolder,mainfolder = folders.split(',')
        bar.dataController("""
            SET #FORM.imgFolders = useMainFolder? mainfolder+'/'+ticket_id+'/images':customfolder+'/'+ticket_id+'/images';
            """,useMainFolder='^.record.mainfolder',ticket_id='^.record.__ticket_id',
            customfolder=customfolder,mainfolder=mainfolder)
        palette = bar.imgPick.imgPickerPalette(code='_ticket_img_picker',folders='^#FORM.imgFolders',
                                                dockButton_iconClass='iconbox note')
        form.dataController("""var dlg = this.getParentWidget('dialog');
                                if(dlg.open){
                                    if(setting){
                                        this._snapshot_hidden = true;
                                        dlg.hide();
                                    }
                                }
                                if(this._snapshot_hidden && !setting){
                                    delete this._snapshot_hidden;
                                    dlg.show();
                                }
                                """,subscribe_onPageSnapshot=True)
        palette.dataController("this.getParentWidget('floatingPane').hide()",formsubscribe_onDismissed=True)

    def tk_struct_ticket(self,struct):
        r = struct.view().rows()
        r.cell('title',width='20em',name='!!Title')
        r.cell('ticket_type',width='10em',name='!!Type',values='B:Bug,C:Cosmetic,F:Feature Request')
        #r.cell('description',width='30em',name='!!Description')
        r.cell('date',dtype='D',width='5em',name='!!Date')
        r.cell('created_by',width='8em',name='Created by')
        r.cell('assigned_to',width='8em',name='Assigned to')
        r.cell('status',width='10em',name='!!Status',values='N:New,P:In progress,S:Solved')

    @public_method
    @extract_kwargs(default=True)
    def tk_loadTicket(self,path=None,default_kwargs=None,**kwargs):
        resultAttr = dict()
        result = Bag()
        if path == '*newrecord*':
            content = Bag(default_kwargs)
            content['created_by'] = self.user
            content['date'] = self.workdate
            content['__ticket_id'] = self.getUuid()
            content['__ins_ts'] = datetime.now()
        else:
            content = Bag(path)
        if content['created_by'] != self.user \
           and not ('superadmin' in self.userTags or '_DEV_' in self.userTags):
            resultAttr['_protect_write'] = True
        result.setItem('content',content,resultAttr)
        return result

    @public_method
    def tk_deleteTicketRows(self,files=None,**kwargs):
        if isinstance(files,basestring):
            files = files.split(',')
        for f in files:
            shutil.rmtree(os.path.dirname(f))

    def tk_ticketFolder(self,useMainFolder=False,allFolders=None):
        if self.ticket_path:
            return self.ticket_path
        elif self.maintable:
            tbllist = self.maintable.split('.')
            pkg = self.package.name
            tblpkg = tbllist[0]
            mainpath = os.path.join('pkg:%s' %tblpkg,'tickets','tables',tbllist[1])
            if tblpkg==pkg or useMainFolder:
                return mainpath
            custompath = os.path.join('pkg:%s' %pkg,'tickets',
                    'tables','_packages',tbllist[0],tbllist[1])
            if allFolders:
                return ','.join([custompath,mainpath])
            return custompath

    def tk_getTicketPath(self,ticket_id,useMainFolder):
        return os.path.join(self.tk_ticketFolder(useMainFolder=useMainFolder),ticket_id)

    @public_method
    def tk_saveTicket(self,path=None,data=None,**kwargs):
        removing_path = None
        newpath = self.site.getStaticPath(self.tk_getTicketPath(data['__ticket_id'],data['mainfolder']))
        if path=='*newrecord*':
            data['__mod_ts'] = data['__ins_ts']
            path = newpath
        else:
            data['__mod_ts'] = datetime.now()
        if path!=newpath:
            removing_path = path
            path = newpath
            shutil.copytree(removing_path,path)
            shutil.rmtree(removing_path)
        if not os.path.exists(path):
            os.makedirs(path)
        filepath = os.path.join(path,'ticket.xml')
        data.toXml(filename=filepath)
        return dict(path=filepath)

    @public_method
    def tk_checkFilePermission(self,filesbag,**kwargs):
        if 'superadmin' in self.userTags or '_DEV_' in self.userTags:
            return 
        for n in filesbag:
            if n.attr['created_by']!=self.user:
                n.attr['_is_readonly_row'] = True


