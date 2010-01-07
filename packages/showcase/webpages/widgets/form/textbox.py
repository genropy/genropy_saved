#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#
#  untitled
#
#  Created by Giovanni Porcari on 2007-03-24.
#  Copyright (c) 2007 Softwell. All rights reserved.
#

"""textbox"""
import os

import datetime
from gnr.core.gnrbag import Bag, DirectoryResolver

class GnrCustomWebPage(object):
    def main(self, root, **kwargs):
        fb = root.form().formbuilder(datapath='form',cols=3)
        fb.textBox(value='^.r0.name',lbl='Name one')
        fb.textbox(value='^code',connect_onkeyup="""if($1.target.value.length==5){
                                                        var form = $1.target.form;
                                                        var pos = dojo.indexOf(form.elements,$1.target)
                                                        form.elements[pos+1].focus();
                                                    }""")
        root.dataController("console.log('carico il record '+code)",code="^code")
        fb.numberTextBox(value='^.r0.age',lbl='age')
        fb.dateTextBox(value='^.r0.birthday',lbl='Birthday')        
        fb.dateTextBox(value='^.r0.date',lbl='date')
        fb.dateTextBox(value='^.r0.dob',lbl='DOB',popup=False)

