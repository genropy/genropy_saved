#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-

class GnrCustomWebPage(object):
    def main(self, root, **kwargs):
        fb = root.formbuilder(cols=2)
        fb.data('base',0)
        fb.data('height',0)
        fb.horizontalSlider(lbl='!!Base', value='^base', width='200px',
                            minimum=0, maximum=100)
        fb.numberTextBox(value='^base', places=2)
        fb.horizontalSlider(lbl='!!Height', value='^height', width='200px',
                            minimum=0, maximum=100)
        fb.numberTextBox(value='^height', places=2)
        
        fb.dataFormula('area', 'base * altezza', base='^base', altezza='^height')
        
        fb.dataRpc('area_server', 'calcoloArea', base='^base', height='^height',
                    _fired='^do_rpc', _if='_fired&&(base >= 0) && (height >= 0)', _else='return "** No Server Call**"')
        
        fb.div(lbl='!!Area', value='^area', border='2px solid grey',padding='2px')
        fb.div(lbl='!!Area Rpc', value='^area_server', border='2px solid green',padding='2px')
        fb.div()    
        fb.checkbox(value='^do_rpc', label='Calculated Server Area')      
        
    def rpc_calcoloArea(self,base,height):
        return base*height