# -*- coding: UTF-8 -*-

# th_form.py
# Created by Francesco Porcari on 2011-05-04.
# Copyright (c) 2011 Softwell. All rights reserved.


from gnr.web.gnrwebstruct import struct_method
from gnr.core.gnrlang import extract_kwargs
from gnr.web.gnrbaseclasses import BaseComponent


class TableHandlerForm(BaseComponent):
    py_requires="gnrcomponents/formhandler:FormHandler"

    @extract_kwargs(dialog=True,palette=True,default=True)
    @struct_method
    def th_tableEditor(self,pane,frameCode=None,table=None,th_pkey=None,formResource=None,
                        dialog_kwargs=None,palette_kwargs=None,default_kwargs=None,formInIframe=False,readOnly=False,**kwargs):
        form = pane.view.grid.linkedForm(frameCode=frameCode,
                                 th_root=frameCode,
                                 datapath='.form',
                                 childname='form',
                                 table=table,
                                 formResource=formResource,
                                 dialog_kwargs=dialog_kwargs,
                                 palette_kwargs=palette_kwargs,
                                 default_kwargs=default_kwargs,
                                 iframe=formInIframe,
                                 **kwargs) 
        if formInIframe:
            return form
        slots = 'navigation,|,5,*,|,semaphore,|,formcommands,|,dismiss,5,locker,5'
        if readOnly:
            slots = 'navigation,|,5,*,|,dismiss,5'
        form.top.slotToolbar(slots,dismiss_iconClass='tb_button tb_listview',namespace='form')
        formattr = form.attributes
        table = formattr.get('table')
        frameCode = formattr.get('frameCode')
        self._th_mixinResource(frameCode,table=table,resourceName=formResource,defaultClass='Form')   
        if table == self.maintable and hasattr(self,'th_form'):
            self.th_form(form)
        else:
            self._th_hook('form',mangler=frameCode)(form)
        return form

