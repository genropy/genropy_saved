#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-


class GnrCustomWebPage(object):
    def main(self, root, **kwargs):
        fb = root.formbuilder(cols=2)
        fb.horizontalslider(lbl='!!Base', value = '^base', width='200px', minimum=0, maximum=100,intermediateChanges=True)
        fb.numberTextBox(value='^base', text_align='right', places=2)
        fb.horizontalslider(lbl='!!Height', value = '^height', width='200px', minimum=0, maximum=100,intermediateChanges=True)
        fb.numberTextBox(value='^height', text_align='right', places=2)
        
        fb.dataFormula('area', 'base * height', base='^base', height='^height')
        fb.div(lbl='!!Area', value = '^area')
        
        fb.dataRpc('area_server', 'areaPython', base='^base', height='^height', _rpc='^do_rpc',
                                    _if='_rpc', _else='return "niente server"')
        fb.div(lbl='!!Area RPC', value = '^area_server')
        fb.dataFormula('height_cell', "Math.ceil(height)*2+'px'", height='^height')
        fb.dataFormula('lunghezza', "campo.length", campo='^form.record.campo')
        fb.dataFormula('width_cell', "Math.ceil(base)*2+'px'", base='^base')
        d=fb.div(width='^width_cell', height='^height_cell',background='^bgcolor')
        fb.checkbox(value='^do_rpc', label='Calculate server side')
        fb.horizontalslider(lbl='!!Red', value = '^red', width='200px', minimum=0, maximum=255, 
                            discreteValues='256', default_value=128,intermediateChanges=True)
        fb.horizontalslider(lbl='!!Green', value = '^green', width='200px', minimum=0, maximum=255, 
                            discreteValues='256', default_value=128,intermediateChanges=True)
        fb.horizontalslider(lbl='!!Blue', value = '^blue', width='200px', minimum=0, maximum=255,
                            discreteValues='256', default_value=128,intermediateChanges=True)
        fb.dataFormula('bgcolor', "'#'+red.toString(16)+green.toString(16)+blue.toString(16)", 
                                red='^red', green='^green', blue='^blue',_init=True)
        fb.textbox(value='^bgcolor')
        
        #with inline javascript expression
        # == means evaluate the embedded javascript
        d=fb.div(width='^width_cell', height='^height_cell', red='^red', green='^green', blue='^blue',
                background="=='#'+red.toString(16)+green.toString(16)+blue.toString(16)")
        
     
    def rpc_areaPython(self, base, height):
        base = base or 0
        height = height or 0
        return base * height
            
