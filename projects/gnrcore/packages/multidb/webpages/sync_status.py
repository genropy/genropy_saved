# -*- coding: UTF-8 -*-

# untitled.py
# Created by Francesco Porcari on 2011-02-02.
# Copyright (c) 2011 Softwell. All rights reserved.

class GnrCustomWebPage(object):
    py_requires='public:Public'

    def pageAuthTags(self, method=None, **kwargs):
        return 'admin'
        
    def windowTitle(self):
        return '!!Sync status'
         
    def main(self, rootBC, **kwargs):
        """
        mostra una grid sopra con tablename, #elementi inseriti
        #elementi cancellati e modificati
        
        tre grid sotto con inseriti, modificati, cancellati analiticamente
        per ogni grid abbiamo id, rowcaption operatore data e ora
        per modificati anche la modifica
        """
        pane = self.pbl_rootContentPane(rootBC,title='!!Sync Status',datapath='syncstatus')
        frame = pane.framePane(frameCode='syncstatus')
        frame.includedView(storepath='.current')
        frame.dataRpc('.current','getCurrentStatus')
    
    def rpc_getCurrentStatus(self):
        """
        per ogni table che è in sync
        prende l'ultima data di inserimento e l'ultima data di variazione nel 
        db corrente e cerca tutti i record nel db base con data inserimento e data variazione
        e ottiene, per ipotesi tre record modificati e 2 inseriti
        """
        pass
        