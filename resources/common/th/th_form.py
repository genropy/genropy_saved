# -*- coding: UTF-8 -*-

# th_form.py
# Created by Francesco Porcari on 2011-05-04.
# Copyright (c) 2011 Softwell. All rights reserved.


from gnr.web.gnrwebstruct import struct_method
from gnr.web.gnrbaseclasses import BaseComponent
from gnr.core.gnrdecorator import extract_kwargs
from gnr.core.gnrstring import boolean


class TableHandlerForm(BaseComponent):
    py_requires="gnrcomponents/formhandler:FormHandler,gnrcomponents/batch_handler/batch_handler:TableScriptHandlerCaller"

    @struct_method
    def th_tableEditor(self,pane,frameCode=None,table=None,th_pkey=None,formResource=None,
                        formInIframe=False,readOnly=False,**kwargs):
        table = table or pane.attributes.get('table')
        self._th_mixinResource(frameCode,table=table,resourceName=formResource,defaultClass='Form') 
        options = self._th_hook('options',mangler=frameCode,dflt=dict())()
        options['readOnly'] = options.get('readOnly',readOnly)
       #slots = '*,|,semaphore,|,formcommands,|,dismiss,5,locker,5'
       #options['slots'] = options.get('slots',slots)
        options.update(kwargs)
        form = pane.view.grid.linkedForm(frameCode=frameCode,
                                 th_root=frameCode,
                                 datapath='.form',
                                 childname='form',
                                 table=table,
                                 formResource=formResource,
                                 iframe=formInIframe,
                                 **options) 
        if formInIframe:
            return form
        self._th_applyOnForm(form,options=options,mangler=frameCode)   
        if table == self.maintable and hasattr(self,'th_form'):
            self.th_form(form)
        else:
            self._th_hook('form',mangler=frameCode)(form)
        return form

    @extract_kwargs(default=True,store=True,dialog=True,palette=True)
    @struct_method
    def th_thFormHandler(self,pane,formId=None,table=None,formResource=None,startKey=None,formCb=None,datapath=None,
                        store_kwargs=None,default_kwargs=None,dialog_kwargs=None,palette_kwargs=None,**kwargs):
        tableCode = table.replace('.','_')
        formId = formId or tableCode
        self._th_mixinResource(formId,table=table,resourceName=formResource,defaultClass='Form')
        resource_options = self._th_hook('options',mangler=formId,dflt=dict())()
        resource_options.update(kwargs)
        formroot = pane._makeFormRoot(formId,dialog_kwargs=dialog_kwargs,palette_kwargs=palette_kwargs,form_kwargs=kwargs,datapath=datapath)
        if formroot is None:
            formroot = formroot or pane
        form = formroot.frameForm(frameCode=formId,formId=formId,table=table,
                             store_startKey=startKey,
                             datapath='.form',store='recordCluster',store_kwargs=store_kwargs,**kwargs)
        self._th_applyOnForm(form,options=resource_options,mangler=formId)
        formCb = formCb or self._th_hook('form',mangler=formId)
        form.store.handler('load',default_kwargs=default_kwargs)
        formCb(form)
        return form
        
    def _th_applyOnForm(self,form,options=None,mangler=None):
        showtoolbar = boolean(options.pop('showtoolbar',True))
        navigation = options.pop('navigation',None)
        readOnly = options.get('readOnly')
        form.dataController("""genro.dlg.alert(msg+' '+this.form.getRecordCaption()+': '+(reason=='invalid'?invalid:nochange),titledialog);""",
                            reason="^.controller.save_failed",_if='reason',
                            titledialog='!!Save failed',
                            msg='!!You cannot save',
                            invalid='!!Invalid record',
                            nochange='!!No change to save')
        if form.store.attributes.get('storeType') == 'Collection':
            if navigation is not False:
                navigation = True
        if readOnly:
            slots = '*'
            form.attributes.update(form_readOnly=True)
        if options.get('modal'):
            slots='revertbtn,*,cancel,savebtn'
            form.attributes['hasBottomMessage'] = False
            bar = form.bottom.slotBar(slots,margin_bottom='2px',_class='slotbar_dialog_footer')
            bar.revertbtn.button('!!Revert',action='this.form.publish("reload")',disabled='^.controller.changed?=!#v')
            bar.cancel.button('!!Cancel',action='this.form.publish("navigationEvent",{command:"dismiss"});')
            bar.savebtn.button('!!Save',iconClass='fh_semaphore',action='this.form.publish("save",{destPkey:"*dismiss*"})')    
        elif showtoolbar:
            default_slots = '*,form_delete,form_add,form_revert,form_save,semaphore,locker'
            if navigation:
                default_slots = 'navigation,%s' %default_slots
            elif options.get('selector'):
                default_slots = default_slots.replace('*','5,form_selectrecord,*')
            if options.get('printMenu'):
                default_slots = default_slots.replace('form_delete','form_print,100,form_delete')
            if options.get('linker'):
                default_slots = default_slots.replace('form_delete','')
                default_slots = default_slots.replace('form_add','')
                default_slots = default_slots.replace('locker','')            
            slots = options.get('slots',default_slots)
            form.top.slotToolbar(slots)   
        if not options.get('showfooter',True):
            form.attributes['hasBottomMessage'] = False
        for side in ('top','bottom','left','right'):
            hooks = self._th_hook(side,mangler=mangler,asDict=True)
            for hook in hooks.values():
                hook(getattr(form,side))
        form.store.handler('load',onLoadingHandler=self._th_hook('onLoading',mangler=mangler))
        form.store.handler('save',onSavingHandler=self._th_hook('onSaving',mangler=mangler),
                                 onSavedHandler=self._th_hook('onSaved',mangler=mangler))
            
    
    @struct_method          
    def th_slotbar_form_print(self,pane,**kwargs):
        inattr = pane.getInheritedAttributes()
        table = inattr['table']
        pane.div(_class='iconbox print').menu(modifiers='*',storepath='.resources.print.menu',
                    action="""
                            var kw = objectExtract(this.getInheritedAttributes(),"batch_*",true);
                            kw.resource = $1.resource;
                            if($1.template_id){
                                kw.extra_parameters = new gnr.GnrBag({template_id:$1.template_id,table:kw.table});
                                kw.table = null;
                            } 
                            kw['pkey'] = this.form.getCurrentPkey();
                            genro.publish("table_script_run",kw)
                            """,
                    batch_table=table,batch_res_type='print',
                    batch_sourcepage_id=self.page_id)
        pane.dataRemote('.resources.print.menu',self.th_printMenu,table=table,cacheTime=5)
