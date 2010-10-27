#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-

#  Created by Giovanni Porcari on 2007-03-24.
#  Copyright (c) 2007 Softwell. All rights reserved.

class GnrCustomWebPage(object):
    js_requires='raphael/raphael,raphael/colorpicker,raphael/colorwheel'
    def windowTitle(self):
        return '!!Colorpicker'
        
    def main(self, root, **kwargs):
        tc = root.tabContainer()
        pane1 = tc.contentPane(title='Colorpicker 1')
        self.colorpicker1(pane1)
        
    def colorpicker1(self,pane):
        pane.div('!!Color')
        pane.data('color',"#eeeeee")
        pane.textBox(value="^color",background_color='^color')
        
        pane.dataController("""var out = document.getElementById("output");
                               var cp = Raphael.colorpicker(40, 100, 200, "#eee");
                               var cp2 = Raphael.colorwheel(250, 100, 200, "#eee");
                               // assigning onchange event handler
                               out.onkeyup = cp.onchange = cp2.onchange = function (clr) {
                               clr = this == out ? this.value : clr;
                               genro.setData('color',clr)
                               out.value = clr;
                               this != cp && cp.color(clr);
                               this != cp2 && cp2.color(clr);
                               out.style.background = clr;
                               out.style.color = Raphael.rgb2hsb(clr).b < .5 ? "#fff" : "#000";
                               };""",_onStart=True)
                        
        pane.input(type="text",id="output",value="#eeeeee")