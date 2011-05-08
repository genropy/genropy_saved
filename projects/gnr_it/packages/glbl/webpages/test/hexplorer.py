# -*- coding: UTF-8 -*-

# hexplorer.py
# Created by Francesco Porcari on 2010-12-15.
# Copyright (c) 2010 Softwell. All rights reserved.

"HEXPLORER"
class GnrCustomWebPage(object):
    py_requires="gnrcomponents/testhandler:TestHandlerFull,gnrcomponents/palette_manager:PaletteManager"
    
    def windowTitle(self):
        return ''
         
    def test_0_default_dock(self,pane):
        pane.dock(id='default_dock')
        
    def provincia_struct(self,struct):
        r = struct.view().rows()
        r.fieldcell('sigla',width='5em')
        r.fieldcell('nome',width='15em')
        r.fieldcell('@regione.nome',width='15em')
        
    def test_0_grid(self,pane):
        pane.paletteGrid('province',title='Province',
                        configurable=True,struct='regione',
                        table='glbl.provincia',searchOn='*A,T,D').selectionStore(gridId='province_grid')
                        
   #def test_2_analyze(self,pane):
   #    """Test hexplorer"""
   #    pane.paletteTree('localita',title='!!Localita Geo',searchOn=True).tableAnalyzeStore(table='glbl.localita',#where="$nome ILIKE :chunk",chunk='%%u%%',
   #                    group_by=['@provincia.@regione.zona','@provincia.@regione.nome','@provincia.nome',self.iniziale,'$nome'],
   #                    order_by='@provincia.@regione.ordine,$nome')
        
    def iniziale(self,value):
        return value['nome'][0]