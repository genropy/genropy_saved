#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#
#

class GnrCustomWebPage(object):
    def main(self, root, **kwargs):
        fb=root.formbuilder(cols="3", cellspacing='10')
        fb.button('Set',action="FIRE setmessage;")
        fb.textbox(lbl='Addr:', value='^record.addrsent')
        fb.textbox(lbl='Content:', value='^record.contentsent', autowidth=2)
        fb.button('Get',action="FIRE getmessage;")
        fb.textbox(lbl='Addr:', value='^record.addrgot')
        fb.textbox(lbl='Content:', value='^record.contentgot', autowidth=2)
        root.dataRpc('dummy', 'setMsg', key='=record.addrsent',value='=record.contentsent', _fired='^setmessage')
        root.dataRpc('record.contentgot', 'getMsg', key='=record.addrgot', _fired='^getmessage')
        
    def rpc_getMsg(self, key=None):
        result = self.site.shared_data.get(key)
        return result
        
    def rpc_setMsg(self, key=None, value=None):
        return self.site.shared_data.set(key, value)