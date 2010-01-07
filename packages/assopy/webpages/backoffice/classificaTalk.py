#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#
#  Registrazione nuovo utente
#
#  Created by Francesco Cavazzana on 2008-01-23.
#

""" Registrazione nuovo utente """
import datetime
import os

from gnr.core.gnrstring import templateReplace
from gnr.core.gnrbag import Bag

# --------------------------- GnrWebPage subclass ---------------------------
class GnrCustomWebPage(object):
    py_requires='basecomponent:Public'
    def windowTitle(self):
         return '!!Assopy Classifica Talk'
         
    def pageAuthTags(self, method=None, **kwargs):
         return 'superadmin'
        
    def main(self, root, userid=None,**kwargs):
        self.controller(root)
        lc,top = self.publicRoot(root)
        top.div('!!Classifica Talk')
        sp = lc.splitContainer(layoutAlign='client')
        left=sp.accordionContainer(sizeShare=25)
        right=sp.contentPane(sizeShare=25)
        talkpane=left.accordionPane(title='Per Talk')
        sociopane=left.accordionPane(title='Per Socio')
        talkpane.tree(storepath='totalizers',
                   inspect='shift', selectedPath='aux.selected_talk', label="Talks")
        sociopane.tree(storepath='totalizers.per_socio',
                   inspect='shift', selectedPath='aux.selected_socio', label="Soci")
        
    def controller(self,pane):
        pane.dataSelection('classifica', 'assopy.valutazione', 
                        selectmethod='analisiVoti',
                        _fired='^aux.startClassifica',
                        _onResult='FIRE aux.endClassifica=true;',
                        sync=True,
                        selectionName='*classifica', recordResolver=False, _init=True)
        pane.dataRpc('totalizers', 'totalizers', _fired='^aux.endClassifica')
                        
    def rpc_analisiVoti(self, **kwargs):
        return self.db.table('assopy.valutazione').creaClassifica()

    def rpc_totalizers(self):
        selection = self.unfreezeSelection(self.db.table('assopy.valutazione'), 'classifica')
        return selection.totalizer()
        
    def rpc_righeTalk(self, pkey):
        selection = self.unfreezeSelection(self.db.table('assopy.valutazione'), 'classifica')
        return selection.output('grid', subtotal_rows='per_talk.%s' % pkey, recordResolver=False)
        
    def rpc_righeSocio(self, pkey):
        selection = self.unfreezeSelection(self.db.table('assopy.valutazione'), 'classifica')
        return selection.output('grid', subtotal_rows='per_socio.%s' % pkey, recordResolver=False)

def index(req, **kwargs):
    return GnrWebPage(req, GnrCustomWebPage, __file__, **kwargs).index()
