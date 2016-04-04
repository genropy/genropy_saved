from gnr.web.gnrwebpage import BaseComponent
from gnr.web.gnrwebstruct import struct_method
from gnr.core.gnrdecorator import public_method,extract_kwargs
from gnr.core.gnrbag import Bag
from datetime import datetime
import os
import shutil


class TicketHandler(BaseComponent):
    py_requires ='th/th:TableHandler'

    @struct_method
    def tk_ticketFrame(self,pane,project_code=None,package_identifier=None,table_identifier=None,pagename=None,**kwargs):
        print 'project_code',project_code,'package_identifier',package_identifier,'table_identifier',table_identifier
        pane.dialogTableHandler(table='uke.ticket',dbstore='@uke',formResource='FormExternal',
                                condition="""$instance_id=:instance_id AND 
                                             $pagename=:pagename AND
                                             $table_identifier=:table_identifier AND 
                                             $package_identifier=:package_identifier AND
                                             $project_code=:project_code""",
                                view_store__ticketrun='^tickets.run',
                                condition_instance_id=self.site.ukeInstanceId,
                                condition_pagename=pagename,
                                condition_package_identifier=package_identifier,
                                condition_table_identifier=table_identifier,
                                condition_project_code=project_code,
                                default_username=self.user,
                                default_instance_id=self.site.ukeInstanceId,
                                default_pagename=pagename,
                                default_project_code=project_code,
                                default_package_identifier=package_identifier,
                                default_table_identifier=table_identifier)
        pane.dataRpc('dummy',self.tk_checkTicketInfo,project_code=project_code,table_identifier=table_identifier,pagename=pagename,
                                package_identifier=package_identifier,_fired='^tickets.run')

    @public_method
    def tk_checkTicketInfo(self,project_code=None,package_identifier=None,table_identifier=None,pagename=None):
        ukeinstance = self.application.getAuxInstance('uke')
        def insertIfNotExist(table,pkey,**kwargs):
            tblobj = ukeinstance.db.table(table)
            if not tblobj.existsRecord(pkey):
                record = {tblobj.pkey:pkey}
                record.update(kwargs)
                tblobj.insert(record)
                print 'inserted record',record,table
        insertIfNotExist('uke.project',project_code)
        if package_identifier:
            insertIfNotExist('uke.package',package_identifier,code=package_identifier.split('/')[-1],project_code=project_code)
        if table_identifier:
            insertIfNotExist('uke.pkgtable',table_identifier,project_code=project_code,
                                            package_identifier=package_identifier,
                                            name=table_identifier.split('/')[-1])
        ukeinstance.db.commit()


    def onMain_ticket_handler(self):
        pane = self.pageSource()
        pane.data('gnr.table',self.maintable)
        pane.data('gnr.project_code',self.db.application.packages[self.package.name].project)
        pane.script("""genro.ticketHandler = {
                getTicketInfo:function(){
                    var project_code = genro.getData('gnr.project_code');
                    var package_identifier = project_code+'/'+genro.getData('gnr.package');
                    var result = {
                        project_code:project_code,
                        package_identifier:package_identifier,
                        table_identifier:package_identifier+'/'+genro.getData('gnr.table'),
                        pagename:genro.getData('gnr.pagename')
                    };
                    return result;
                }
            }""")

class TicketHandlerFile(BaseComponent):
    py_requires ='gnrcomponents/framegrid:FrameGrid,gnrcomponents/formhandler:FormHandler,gnrcomponents/filepicker:FilePicker'
    ticket_path = ''

    def onMain_ticket_handler(self):
        pane = self.pageSource()
        pane.data('gnr.tickets.allFolders',self.tk_ticketFolder(allFolders=True))
        pane.script("""genro.ticketHandler = {
                getTicketFolders:function(){
                    return genro.getData('gnr.tickets.allFolders');
                }
            }""")

    @struct_method
    def tk_ticketFrame(self,pane,code=None,folders=None,**kwargs):
        view = pane.frameGrid(frameCode='V_ticketframe_%s' %code,struct=self.tk_struct_ticket,
                                    autoToolbar=False,
                                    datapath='.view',grid_rowStatusColumn=True,**kwargs)
        view.top.slotToolbar('*,delrow,addrow,viewlocker,5')
        fstore = view.grid.fsStore(childname='store',
                                    folders=folders,
                                    include='ticket.xml',
                                    applymethod=self.tk_checkFilePermission,
                                    deletemethod=self.tk_deleteTicketRows)
        view.dataController("fstore.store.loadData();fstore.store.setLocked(true)",fstore=fstore,folders=folders)
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
        form.store.handler('save',rpcmethod=self.tk_saveTicket,folderpath=folders.replace('^','='))
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
        #tbllist = self.maintable.split('.')
       #pkg = self.package.name
       #tblpkg = tbllist[0]
       #if pkg!=tblpkg and self.isDeveloper():
       #    
        if self.isDeveloper():
            fb.checkbox('^.mainfolder',label='In original package')
        center = bc.framePane(frameCode='ticketDesc',region='center')
        bar =center.top.slotToolbar('2,ctitle,*,imgPick,2',ctitle='!!Description')
        center.simpleTextArea(value='^.record.description',editor=True)
       #customfolder,mainfolder = None,None
       #if ',' in folders:
       #    customfolder,mainfolder = folders.split(',')
       #else:
       #    mainfolder = folders
        bar.dataController("""
            var fldlist = folders.split(',');
            var customfolder,mainfolder;
            if(fldlist.length>1){
                customfolder = fldlist[0];
                mainfolder = fldlist[1];
            }else{
                mainfolder = folders;
            }
            SET #FORM.imgFolders = (useMainFolder || !customfolder)? mainfolder+'/'+ticket_id+'/images':customfolder+'/'+ticket_id+'/images';
            """,useMainFolder='^.record.mainfolder',ticket_id='^.record.__ticket_id',folders=folders.replace('^','='))
        palette = bar.imgPick.imgPickerPalette(code='_ticket_img_picker',folders='^#FORM.imgFolders',
                                                dockButton_iconClass='iconbox note',externalSnapshot=True)
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

    #def tk_getTicketPath(self,ticket_id,useMainFolder):
    #    return os.path.join(self.tk_ticketFolder(useMainFolder=useMainFolder),ticket_id)

    @public_method
    def tk_saveTicket(self,path=None,data=None,folderpath=None,**kwargs):
        removing_path = None
        mainfolder = None
        if ',' in folderpath:
            folderpath,mainfolder = folderpath.split(',')
        if data['mainfolder'] and mainfolder:
            folderpath = mainfolder
        ticket_path = os.path.join(folderpath,data['__ticket_id'])  # self.tk_getTicketPath(data['__ticket_id'],data['mainfolder'])
        newpath = self.site.getStaticPath(ticket_path)
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


