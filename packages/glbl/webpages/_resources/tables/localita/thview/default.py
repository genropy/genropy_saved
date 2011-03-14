# -*- coding: UTF-8 -*-

# base.py
# Created by Francesco Porcari on 2011-03-13.
# Copyright (c) 2011 Softwell. All rights reserved.

from gnr.web.gnrbaseclasses import BaseComponent
class Main(BaseComponent):
    
    def lstBase(self,struct):
        r = struct.view().rows()
        r.fieldcell('nome',width='50%')
        r.fieldcell('provincia',width='20%')
        r.fieldcell('codice_istat',width='10%') 
        r.fieldcell('codice_comune',width='10%')
        r.fieldcell('prefisso_tel',width='5%')
        r.fieldcell('cap',width='5%')
        
    def orderBase(self):
        return 'nome'
        
    def queryBase(self):
        return dict(column='nome',op='contains', val=None)