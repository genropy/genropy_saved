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

from gnr.web.gnrwebpage import GnrWebPage
import datetime
from gnr.core.gnrbag import Bag, DirectoryResolver
from gnr.web.gnrwebapp import WebPageResolver
# --------------------------- GnrWebPage subclass ---------------------------
class GnrCustomWebPage(object):
    def main(self, root, **kwargs):
        root.data('tree.data',self.treedata())
        root.h1('A simple tree')
        root.tree(storepath='tree.data')
        root.h1('See the attributes with shift mouseover')
        #root.tree(storepath='tree.data',inspect='shift')
        root.tree(storepath='pages',inspect='shift')
        root.data('pages',self.application.webpages)
        
        
    def treedata(self):
        b = Bag()
        b.setItem('person.name','John',job='superhero')
        b['person.age'] = 22
        b.setItem('pet.animal', 'Dog',race='Doberman')
        return b


def index(req, **kwargs):
    return GnrWebPage(req, GnrCustomWebPage, __file__, **kwargs).index()
