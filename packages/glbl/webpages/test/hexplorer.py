# -*- coding: UTF-8 -*-

# hexplorer.py
# Created by Francesco Porcari on 2010-12-15.
# Copyright (c) 2010 Softwell. All rights reserved.

"HEXPLORER"
class GnrCustomWebPage(object):
    py_requires="gnrcomponents/testhandler:TestHandlerFull,gnrcomponents/explorer_manager:ExplorerManager"
    
    def windowTitle(self):
        return ''
         
    def test_0_firsttest(self,pane):
        """Test hexplorer"""
        self.tableTreeExplorer(pane,table='glbl.localita',where="$nome ILIKE :chunk",chunk='%%u%%',
                        group_by=['@provincia.@regione.zona','@provincia.@regione.nome','@provincia.nome',self.iniziale,'$nome'],
                        order_by='@provincia.@regione.ordine,$nome')
        
    def iniziale(self,value):
        return value['nome'][0]
        
        