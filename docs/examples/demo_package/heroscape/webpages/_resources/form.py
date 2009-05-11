#!/usr/bin/env python
# encoding: utf-8
"""
form.py

Created by Saverio Porcari on 2008-03-23.
Copyright (c) 2008 __MyCompanyName__. All rights reserved.
"""

import sys
import os


class Form(object):
    def pageForm(self,pane):
        self.messagePane(pane)
        self.formController(pane)
        lc=pane.layoutContainer(height='100%')
        self.formToolbar(lc)
        client = lc.contentPane(layoutAlign='client',_class='pbl_formContainerClient tablewiew',nodeId='formPane',
                                margin_top='0px',border_top='0px',datapath='form.record')
        self.formBase(client,disabled='^form.locked')
    
