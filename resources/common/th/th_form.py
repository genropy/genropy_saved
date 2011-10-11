# -*- coding: UTF-8 -*-

# th_form.py
# Created by Francesco Porcari on 2011-05-04.
# Copyright (c) 2011 Softwell. All rights reserved.


from gnr.web.gnrwebstruct import struct_method
from gnr.web.gnrbaseclasses import BaseComponent
from gnr.core.gnrstring import boolean


class TableHandlerForm(BaseComponent):
    py_requires="gnrcomponents/formhandler:FormHandler"

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
        self.th_formOptions(form,options=options)
        for side in ('top','bottom','left','right'):
            hooks = self._th_hook(side,mangler=frameCode,asDict=True)
            for hook in hooks.values():
                hook(getattr(form,side))    
        if table == self.maintable and hasattr(self,'th_form'):
            self.th_form(form)
        else:
            self._th_hook('form',mangler=frameCode)(form)
        return form
        
    def th_formOptions(self,form,options=None):
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
            bar = form.bottom.slotBar(slots,margin_bottom='2px')
            bar.revertbtn.button('!!Revert',action='this.form.publish("reload")',disabled='^.controller.changed?=!#v')
            bar.cancel.button('!!Cancel',action='this.form.publish("navigationEvent",{command:"dismiss"});')
            bar.savebtn.button('!!Save',iconClass='fh_semaphore',action='this.form.publish("save",{destPkey:"*dismiss*"})')    
        elif showtoolbar:
            default_slots = '*,formcommands,semaphore,locker'
            slots = options.get('slots',default_slots)
            if options.get('linker'):
                slots = '*,form_revert,form_save,semaphore'
            if options.get('selector'):
                slots = slots.replace('*','5,form_selectrecord,*')
            if options.get('lockable'):
                slots = slots.replace(slots,'%s,locker' %slots)
            elif navigation:
                slots = 'navigation,%s' %slots
            form.top.slotToolbar(slots)   
        if not options.get('showfooter',True):
            form.attributes['hasBottomMessage'] = False
