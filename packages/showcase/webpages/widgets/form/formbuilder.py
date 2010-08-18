#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#
#  Created by Giovanni Porcari on 2007-03-24.
#  Copyright (c) 2007 Softwell. All rights reserved.

class GnrCustomWebPage(object):
    #   formbuilder - DEFAULT parameters:
    #       border_spacing='6px'
    #       cols=1
    #       fld_width='7em'
    
    css_requires= 'index'
    
    def main(self, root, **kwargs):
        fb=root.formbuilder(cols=3,datapath='first')
        fb.textbox(value='^.name',lbl='Name')
        fb.textbox(value='^.surname',colspan=2,lbl='Surname')
        fb.numberTextbox(value='^.age',width='4em',lbl="Age")
        fb.filteringSelect(value='^.sex',colspan=2,values='M:Male,F:Female',lbl='Sex')
        fb.textbox(value='^.job.profession',lbl='Job')
        fb.textbox(value='^.job.company_name',lbl='Company name')