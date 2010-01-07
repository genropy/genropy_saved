#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#
#  untitled
#
#  Created by Giovanni Porcari on 2007-03-24.
#  Copyright (c) 2007 Softwell. All rights reserved.
#

""" Buttons """
import os
from gnr.core.gnrbag import Bag

# --------------------------- GnrWebPage subclass ---------------------------
class GnrCustomWebPage(object):
    css_requires='button'
    
    def main(self, root, **kwargs):
        root.div("Formbuilder")
        fb=root.formbuilder(cols=2,_class='ppp')
        fb.textbox(lbl='Prova',value='^prova',width='10em')
        fb.textbox(lbl='Pippo',value='^pippo',width='10em')
        fb.textbox(value='^description',lbl="Description",width='30em',colspan="2")
        root.div("tabella semplice")
        table = root.table().tbody()
        r1 = table.tr()
        r1.td('AAA')
        r1.td().textbox(value='^aaa')
        r1.td('BBB')
        r1.td().textbox(value='^bbb')
        r2 = table.tr()
        r2.td('BBB')
        r2.td(colSpan="3",width='30em').textbox(value='^bbb',width='25em')



def index(req, **kwargs):
    return GnrWebPage(req, GnrCustomWebPage, __file__, **kwargs).index()
