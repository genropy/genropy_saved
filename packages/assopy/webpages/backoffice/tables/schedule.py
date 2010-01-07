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

class GnrCustomWebPage(object):
    maintable='assopy.schedule'
    py_requires='basecomponent:Public,standard_tables:TableHandler'
    
    def windowTitle(self):
        return '!!Assopy Schedule'
        
    def pageAuthTags(self, method=None, **kwargs):
        return 'socio'
        
    def tableWriteTags(self):
        return 'admin'
        
    def tableDeleteTags(self):
        return 'superadmin'
        
    def barTitle(self):
        return '!!Gestione Schedulazione'
        
    def columnsBase(self):
        return """nome:12,descrizione:12,data/Data,ora_inizio,ora_fine"""

    def formBase(self,pane,disabled,datapath=''):
        fb = pane.formbuilder(datapath=datapath,cols=1, margin_left='2em',border_spacing='7px',margin_top='1em',disabled=disabled)
        fb.field('assopy.schedule.nome')
        fb.field('assopy.schedule.descrizione', width='30em')
        fb.field('assopy.schedule.luogo')
        fb.DateTextBox(value='^.data',lbl='Data',disabled=disabled)
        fb.TimeTextBox(value='^.ora_inizio',lbl='Dalle',disabled=disabled)
        fb.TimeTextBox(value='^.ora_fine',lbl='Alle',disabled=disabled)
        fb.field('assopy.schedule.durata')
        fb.field('assopy.schedule.talk_id',auxColumns='durata',width='30em',selected_durata='^.durata')

    def orderBase(self):
        return 'data'
    
    def queryBase(self):
        return dict(column='nome',op='contains',val=None)
    
    def rpc_save(self,data=None,**kwargs):
        self.tblobj.insertOrUpdate(data)
        self.db.commit()
        return ('ok',dict(_pkey=data[self.tblobj.pkey]))
    
