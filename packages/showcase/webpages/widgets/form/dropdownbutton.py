#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#
#  Created by Giovanni Porcari on 2007-03-24.
#  Copyright (c) 2007 Softwell. All rights reserved.

""" dropdownbutton """
import os
from gnr.core.gnrbag import Bag

class GnrCustomWebPage(object):

    def main(self, root, **kwargs):
        root.data('contents', self._receiptBag())
        root.data('label','contents')
      #x=root.toolbar().dropdownbutton('^label',id='zzz').menu(storepath='contents',
      #                                               action='SET label=this.attr.label')
        x=root.div(height='40px',width='40px',background='red').menu(storepath='contents',modifiers='*',
                                                                    action='alert(this.attr.label)')
        
    def _receiptBag(self):
        b = Bag()
        b.setItem('r1',None,page=0,label='Credit Card')
        b.setItem('r1.aaa',None,label='xxx')
        b.setItem('r2',None,page=1,label='EFTPOS')
        b.setItem('r3',None,page=2,label='Cheque')
        b.setItem('r4',None,page=3,label='Cash')
        b.setItem('r5',None,page=4,label='Journal Transfer')
        b.setItem('r6',None,page=5,label='Credit Note')
        b.setItem('r7',None,page=6,label='Request for Invoice')
        b.setItem('r8',None,page=7,label='Money Order')
        b.setItem('r9',None,page=8,label='Other')
        return b