#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-

#  Created by Giovanni Porcari on 2007-03-24.
#  Copyright (c) 2007 Softwell. All rights reserved.

from gnr.core.gnrbag import Bag

class GnrCustomWebPage(object):
    def main(self, root, **kwargs):
        root.data('contents', self.receiptBag())
        ddb=root.toolbar().dropdownbutton(label='!!Menu').menu(storepath='contents',action=("alert($1.label)"))
        
    def receiptBag(self):
        bag = Bag()
        bag2 = Bag()
        bag2['drag']=['foo']
        bag.setItem('r1',None,page=0,label='Credit Card')
        bag.setItem('r1.aaa','A Bag value',label='Buy')
        bag.setItem('r2',None,label='EFTPOS')
        bag.setItem('r3',None,label='Cheque')
        bag.setItem('r4',None,label='Cash')
        bag.setItem('r5','Another Bag value',label='Journal Transfer')
        bag.setItem('r6',None,label='Credit Note')
        bag.setItem('r7',None,label='Request for Invoice')
        bag.setItem('r8',None,label='Money Order')
        bag.setItem('r9',bag2,label='Other')
        return bag