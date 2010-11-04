#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-

class GnrCustomWebPage(object):
    def test_1_miscellaneous(self, root, **kwargs):
        fb = root.formbuilder(cols=4)
        fb.horizontalslider(lbl='!!Base',value ='^base',
                            minimum=0,maximum=100,intermediateChanges=True,colspan=2)
        fb.numberTextBox(value='^base',places=2,colspan=2)
        fb.horizontalslider(lbl='!!Height',value ='^height',
                            minimum=0,maximum=100,intermediateChanges=True,colspan=2)
        fb.numberTextBox(value='^height',places=2,colspan=2)
        
        fb.horizontalslider(lbl='!!Red',value='^red',width='200px',minimum=0,maximum=255,
                            discreteValues='256',default=128,intermediateChanges=True)
        fb.horizontalslider(lbl='!!Green',value='^green',width='200px',minimum=0,maximum=255,
                            discreteValues='256',default=128,intermediateChanges=True)
        fb.horizontalslider(lbl='!!Blue',value='^blue',width='200px',minimum=0,maximum=255,
                            discreteValues='256',default=128,intermediateChanges=True)
        fb.textbox(value='^bgcolor')
        
        fb.dataFormula('area','base * height',base='^base',height='^height')
        fb.div(lbl='!!Area',value='^area',colspan=4)
        fb.dataRpc('area_server','areaPython',base='^base',height='^height',_rpc='^do_rpc',
                    _if='_rpc', _else='return "** no server call **"')
        fb.div(lbl='!!Area RPC',value='^area_server',colspan=4)
        
        fb.dataFormula('height_cell',"Math.ceil(height)*2+'px'",height='^height')
        fb.dataFormula('lenght',"campo.length", campo='^form.record.campo')
        fb.dataFormula('width_cell',"Math.ceil(base)*2+'px'", base='^base')
        fb.checkbox(value='^do_rpc',label='Calculate server side',colspan=4)
        
        fb.dataFormula('bgcolor',"'#'+red.toString(16)+green.toString(16)+blue.toString(16)",
                        red='^red',green='^green',blue='^blue',_init=True)
        d=fb.div(width='^width_cell',height='^height_cell',background='^bgcolor',colspan=4)
        
        #with inline javascript expression '#' allows to evaluate the embedded javascript
        
        #d=fb.div(width='^width_cell',height='^height_cell',red='^red',green='^green',blue='^blue',
        #        background="=='#'+red.toString(16)+green.toString(16)+blue.toString(16)")
                
    def rpc_areaPython(self, base, height):
        base = base or 0
        height = height or 0
        return base * height