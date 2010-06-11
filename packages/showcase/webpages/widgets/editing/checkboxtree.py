#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#
#  untitled
#
#  Created by Giovanni Porcari on 2007-03-24.
#  Copyright (c) 2007 Softwell. All rights reserved.
#

""" GnrDojo Hello World """
import os

import datetime
from gnr.core.gnrbag import Bag, DirectoryResolver

class GnrCustomWebPage(object):
    def main(self, root, **kwargs):
        root.data('tree.data',self.treedata())
        root.h1('A simple tree')
        root.tree(storepath='tree.data',onChecked=True)
        root.h1('See the attributes with shift mouseover')
        #root.tree(storepath='tree.data',inspect='shift')
        root.tree(storepath='pages',hideValues=True,inspect='shift',onChecked='console.log(node);console.log(event);')
        root.data('pages',Bag(dict(root=DirectoryResolver('/'))))
        
        
    def treedata(self):
        b = Bag()
        b.setItem('person.name','John', job='superhero',checked=True)
        b.setItem('person.age' , 22, checked=False)
        b.setItem('person.sport.tennis' , 'good', checked=False)
        b.setItem('person.sport.footbal' , 'poor', checked=True)
        b.setItem('person.sport.golf' , 'medium', checked=True)
        b.setItem('pet.animal', 'Dog',race='Doberman')
        return b


