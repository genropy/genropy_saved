#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-


class GnrCustomWebPage(object):    
    def main(self, root, **kwargs):
        
        fb = root.formbuilder(cols=2)
        fb.horizontalslider(lbl='!!Base', value = '^base', width='200px', 
                                         minimum=0, maximum=100)
        fb.numberTextBox(value='^base', text_align='right', places=2)
        fb.horizontalslider(lbl='!!Height', value = '^height', width='200px', 
                                         minimum=0, maximum=100)
        fb.numberTextBox(value='^height', text_align='right', places=2)
        fb.dataFormula('area', 'base * height', base='^base', height='^height')
        fb.div(lbl='!!Area', value = '^area',border='1px solid grey',padding='2px')
        
                
        fb.dataRpc('area_server', 'areaPython', base='^base', height='^height', _rpc='^do_rpc',
                                    _if='_rpc&&base&&height', _else='return "** No Server Call**"')                     
        fb.div(lbl='!!Area RPC', value = '^area_server',border='1px solid red',padding='2px')
        fb.div(width='^width', height='^height', background_color='navy', _init=True)
        fb.checkbox(value='^do_rpc', label='Calculate server side')
     
    def rpc_areaPython(self, base, height):
        return base * height
            
def index(req, **kwargs):
    return GnrWebPage(req, GnrCustomWebPage, __file__, **kwargs).index()
