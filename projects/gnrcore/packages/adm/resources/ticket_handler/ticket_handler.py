from gnr.web.gnrwebpage import BaseComponent
from gnr.web.gnrwebstruct import struct_method
from gnr.core.gnrdecorator import public_method,extract_kwargs
from gnr.core.gnrbag import Bag,NetBag
from datetime import datetime
import os
import shutil
import urlparse


class TicketHandler(BaseComponent):
    py_requires ='gnrcomponents/framegrid:FrameGrid,gnrcomponents/formhandler:FormHandler,public:Public'

    @struct_method
    def tk_ticketFrame(self,pane,code='main',project_code=None,
                            package_identifier=None,
                            table_identifier=None,
                            pagename=None,**kwargs):
        view = pane.frameGrid(frameCode='V_ticketframe_%s' %code,struct=self.tk_struct_ticket,
                                    autoToolbar=False,
                                    datapath='.view',grid_rowStatusColumn=True,**kwargs)
        view.top.slotToolbar('*,delrow,addrow,5,viewlocker')
        tstore = view.grid.rpcStore(rpcmethod=self.tk_getCurrentTickets,project_code=project_code,
                        package_identifier=package_identifier,pagename=pagename,
                        table_identifier=table_identifier,
                        #applymethod=self.tk_checkFilePermission,
                        deletemethod=self.tk_deleteTicketRows)


        view.dataController("tstore.store.loadData();tstore.store.setLocked(true)",
                                subscribe_getTickets=True,tstore=tstore)
        form = view.grid.linkedForm(frameCode='F_ticketframe_%s' %code,
                                 datapath='.form',loadEvent='onRowDblClick',
                                 dialog_height='450px',dialog_width='620px',
                                 dialog_title='Ticket',
                                 handlerType='dialog',
                                 childname='form',attachTo=pane)
        self.tk_ticket_form(form,project_code=project_code,
                            package_identifier=package_identifier,
                            table_identifier=table_identifier,
                            pagename=pagename)
        return view

    def tk_ticket_form(self,form,project_code=None,package_identifier=None,table_identifier=None,pagename=None):
        form.store.handler('save',rpcmethod=self.tk_saveTicket)
        helpdesk = self.getPreference('helpdesk',pkg='adm')

        form.store.handler('load',default_project_code=project_code,
                            default_package_identifier=package_identifier,
                            default_table_identifier=table_identifier,
                            default_pagename=pagename,
                            default_client_reference=helpdesk['client_reference'],
                            default_user=self.user,
                            rpcmethod='tk_loadTicket')
        form.top.slotToolbar('2,navigation,*,delete,add,save,semaphore,locker,2')
        bc = form.center.borderContainer()
        fb = bc.contentPane(region='top',padding='10px',datapath='.record').formbuilder(cols=2,border_spacing='3px',
                            colswidth='auto',tdl_padding_left='4px',fld_width='100%')
        fb.filteringSelect(value='^.ticket_type',lbl='Type',
                            values='B:Bug,C:Cosmetic,F:Feature Request',
                            validate_notnull=True)
        fb.filteringSelect(value='^.priority',lbl='Priority',
                            values='1:Low,2:Medium,3:High,4:ASAP',
                            validate_notnull=True)
        fb.textbox(value='^.title',lbl='Title',validate_notnull=True,colspan=3)
 
        center = bc.roundedGroupFrame(title='Description',region='center')
        center.center.contentPane().simpleTextArea(value='^.record.description',editor=True)
        
       #customfolder,mainfolder = None,None
       #if ',' in folders:
       #    customfolder,mainfolder = folders.split(',')
       #else:
       #    mainfolder = folders
       #bar.dataController("""
       #    var fldlist = folders.split(',');
       #    var customfolder,mainfolder;
       #    if(fldlist.length>1){
       #        customfolder = fldlist[0];
       #        mainfolder = fldlist[1];
       #    }else{
       #        mainfolder = folders;
       #    }
       #    SET #FORM.imgFolders = (useMainFolder || !customfolder)? mainfolder+'/'+ticket_id+'/images':customfolder+'/'+ticket_id+'/images';
       #    """,useMainFolder='^.record.mainfolder',ticket_id='^.record.__ticket_id',folders=folders.replace('^','='))
       #palette = bar.imgPick.imgPickerPalette(code='_ticket_img_picker',folders='^#FORM.imgFolders',
       #                                        dockButton_iconClass='iconbox note',externalSnapshot=True)
       #form.dataController("""var dlg = this.getParentWidget('dialog');
       #                        if(dlg.open){
       #                            if(setting){
       #                                this._snapshot_hidden = true;
       #                                dlg.hide();
       #                            }
       #                        }
       #                        if(this._snapshot_hidden && !setting){
       #                            delete this._snapshot_hidden;
       #                            dlg.show();
       #                        }
       #                        """,subscribe_onPageSnapshot=True)
       # palette.dataController("this.getParentWidget('floatingPane').hide()",formsubscribe_onDismissed=True)




    @public_method
    def tk_getCurrentTickets(self,project_code=None,package_identifier=None,
                            table_identifier=None,pagename=None,**kwargs):
        helpdesk = self.getPreference('helpdesk',pkg='adm')
        result = NetBag(self.tk_calcServiceUrl(),'get_tickets',project_code=project_code,
                            client_reference=helpdesk['client_reference'],
                            ticket_reference=table_identifier or pagename)()
        
        return result


    def tk_calcServiceUrl(self):
        helpdesk = self.getPreference('helpdesk',pkg='adm')
        url = helpdesk['url']
        user = helpdesk['user']
        password = helpdesk['password']
        sp = urlparse.urlsplit(url)
        return '%s://%s:%s@%s%s' %(sp.scheme,user,password,sp.netloc,sp.path)
    

    def tk_struct_ticket(self,struct):
        r = struct.view().rows()
        r.cell('date',dtype='D',width='5em',name='!!Date')
        r.cell('title',width='30em',name='!!Title')
        r.cell('ticket_type',width='10em',name='!!Type',values='B:Bug,C:Cosmetic,F:Feature Request')
        r.cell('priority',width='10em',name='!!Priority',values='1:Low,2:Medium,3:High,4:ASAP')
        #r.cell('description',width='30em',name='!!Description')
        r.cell('created_by',width='8em',name='Created by')
        r.cell('assigned_to',width='8em',name='Assigned to')
        r.cell('status',width='10em',name='!!Status',values='N:New,P:In progress,S:Solved')




    @public_method
    @extract_kwargs(default=True)
    def tk_loadTicket(self,pkey=None,default_kwargs=None,**kwargs):
        resultAttr = dict()
        helpdesk = self.getPreference('helpdesk',pkg='adm')
        if pkey=='*newrecord*':
            return Bag(default_kwargs),dict(pkey=pkey,_newrecord=True)

        return NetBag(self.tk_calcServiceUrl(),'load_ticket',pkey=pkey)(),dict(pkey=pkey)

    
    @public_method
    def tk_deleteTicketRows(self,files=None,**kwargs):
        pass


    @public_method
    def tk_saveTicket(self,data=None,**kwargs):
        result = NetBag(self.tk_calcServiceUrl(),'save_ticket',record=data['record'])()
        #return dict(path=filepath)
