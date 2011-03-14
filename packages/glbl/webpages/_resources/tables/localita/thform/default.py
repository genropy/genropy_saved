# -*- coding: UTF-8 -*-

# service_request.py
# Created by Saverio Porcari on 2011-02-15.
# Copyright (c) 2011 __MyCompanyName__. All rights reserved.

from gnr.web.gnrwebpage import BaseComponent

class Main(BaseComponent):
    def formCb(self,parent,**kwargs):
        pane=parent.contentPane(padding='5px',**kwargs).div(_class='pbl_roundedGroup', height='100%')
        pane.div(u'!!Località',_class='pbl_roundedGroupLabel')
        fb = pane.formbuilder(cols=1, margin_left='2em',border_spacing='7px',margin_top='1em')
        fb.field('nome', width='20em')
        fb.field('provincia',width='15em')
        fb.field('prefisso_tel',width='3em')
        fb.field('cap',width='3em')
        fb.field('codice_istat',width='7em')
        fb.field('codice_comune',width='4em')
        
    
    