#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#
#  Created by Giovanni Porcari on 2007-03-24.
#  Copyright (c) 2007 Softwell. All rights reserved.

class GnrCustomWebPage(object):
    css_requires= 'index'
    
    def main(self, root, **kwargs):
        root.div('----- Example of Form builder ------',_class='infopar')
        root.div('note in data source that the following textbox has a RELATIVE path',
                  _class='infopar')
        fb=root.formbuilder(cols=3,datapath='record')
        fb.textbox(value='^.name',lbl='Name')
        fb.textbox(value='^.surname',lbl='Surname',colspan=2)
        fb.numberTextbox(value='^.age',lbl="Age",width='4em')
        fb.filteringSelect(value='^.sex',lbl='Sex',colspan=2,values='M:Male,F:Female')
        fb.textbox(value='^.job.profession',lbl='Job')
        fb.textbox(value='^.job.company_name',lbl='Company name')
        root.div('------ Example of table ------',_class='infopar')
        d = root.div(_class='infopar')
        d.span('What you write in a magic div appear in the other one and vice versa')
        d2 = root.div(_class='infopar') 
        d2.span('The following divs have an ABSOLUTE path')
        table = root.table().tbody()
        r1 = table.tr()
        r1.td('Phone number')
        r1.td().textbox(value='^phone_number')
        r2 = table.tr()
        r2.td('Magic div 1')
        r2.td().textbox(value='^magic')
        r2.td('Magic div 2')
        r2.td().textbox(value='^magic')