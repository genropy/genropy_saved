#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#
#  untitled
#
#  Created by Giovanni Porcari on 2007-03-24.
#  Copyright (c) 2007 Softwell. All rights reserved.
#

""" index.py """

from gnr.web.gnrwebpage import GnrWebPage
from gnr.core.gnrbag import Bag

# --------------------------- GnrWebPage subclass ---------------------------
class GnrCustomWebPage(object):
    py_requires='basecomponent:Public'
    
    def windowTitle(self):
         return '!!Assopy TEST'

    def main(self, root, **kwargs):        
        root.script('genro.querybuilder = new gnr.GnrQueryBuilder("queryroot", "assopy.ordine","querydata")')
        lc = root.layoutContainer(width='100%')
        
        top = lc.contentPane(layoutAlign='top', height='10em')        
        top.textBox(value='^valore', dndTarget='pippo', checkAcceptance='', onDndDrop='alert($1.label)')
        top.button('Query builder', action='genro.querybuilder.buildQueryPane()')
        
        left = lc.contentPane(layoutAlign='left', width='30em', overflow='auto')        
        
        left.dataRemote('_dev.fieldsmenu','app.relationExplorer',table='assopy.ordine',sync=True)
        tree=left.tree(storepath='_dev.fieldsmenu',persist=False,label="Relation Explorer",inspect='shift', labelAttribute='caption',
                       dndController="dijit._tree.dndSource")
                       
        client = lc.contentPane(layoutAlign='client', overflow='auto', padding='1em')        

        client.data('querydata', self.db.table('assopy.ordine').query_test())
        client.data('opmenu',self.dbform.fselect_operators())
        b = Bag()
        b.setItem('and', None, caption='AND')
        b.setItem('or', None, caption='OR')
        
        client.data('jcmenu', b)
        
        b = Bag()
        b.setItem('not', None, caption='NOT')
        b.setItem('yes', None, caption=' - ')
        
        client.data('notmenu', b)
        
        client.div(_class='querygroup', nodeId='queryroot', datapath='querydata')
        
        
        
def index(req, **kwargs):
    return GnrWebPage(req, GnrCustomWebPage, __file__, **kwargs).index()
