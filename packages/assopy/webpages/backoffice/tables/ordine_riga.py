#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#
#  untitled
#
#  Created by Giovanni Porcari on 2007-03-24.
#  Copyright (c) 2007 Softwell. All rights reserved.
#

""" staff """

from gnr.core.gnrbag import Bag

# --------------------------- GnrWebPage subclass ---------------------------
class GnrCustomWebPage(object):
    def pageAuthTags(self, method=None, **kwargs):
        return 'admin'
        
    def main(self, root, **kwargs):
        self.dbform.simpleTableManager(root, table='assopy.ordine_riga')
        

    def lstBase(self,struct):
        r = struct.view().rows()
        r.fieldcell('numero_riga',width='2em',name='Numero')
        r.fieldcell('tipo',width='7em',name='Tipo')
        r.fieldcell('prezzo',width='4em',name='Prezzo')

        return lst

    def formBase(self,pane,datapath=''):

        fb = pane.formbuilder(cols=1)
        fb.field('assopy.ordine_riga.numero_riga')
        fb.field('ordine_id', lbl='Ordine')
        fb.field('tipo')
        fb.field('prezzo')
        
    def orderBase(self):
        return 'numero_riga'
        
    
    def queryBase(self):
        return dict(column='tipo',op='contains', val=None)


def index(req, **kwargs):
    return GnrWebPage(req, GnrCustomWebPage, __file__, **kwargs).index()
