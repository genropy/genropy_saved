# -*- coding: UTF-8 -*-
#--------------------------------------------------------------------------
# Copyright (c) : 2004 - 2007 Softwell sas - Milano 
# Written by    : Giovanni Porcari, Michele Bertoldi
#                 Saverio Porcari, Francesco Porcari , Francesco Cavazzana
#--------------------------------------------------------------------------
#This library is free software; you can redistribute it and/or
#modify it under the terms of the GNU Lesser General Public
#License as published by the Free Software Foundation; either
#version 2.1 of the License, or (at your option) any later version.

#This library is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
#Lesser General Public License for more details.

#You should have received a copy of the GNU Lesser General Public
#License along with this library; if not, write to the Free Software
#Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA


from gnr.web.gnrbaseclasses import BaseComponent

class RemoteBuilder(BaseComponent):
    def buildRemote(self, pane, method, lazy, **kwargs):
        handler = getattr(self, 'remote_%s' % method, None)
        if handler:
            parentAttr = pane.parentNode.getAttr()
            parentAttr['remote'] = 'remoteBuilder'
            parentAttr['remote_handler'] = method
            for k, v in kwargs.items():
                parentAttr['remote_%s' % k] = v
                kwargs.pop(k)
            if not lazy:
                handler(pane, **kwargs)

    def ajaxContent(self, pane, method, **kwargs):
        self.buildRemote(pane, method, False, **kwargs)

    def lazyContent(self, pane, method, **kwargs):
        self.buildRemote(pane, method, True, **kwargs)


class CSSHandler(BaseComponent):
    def cssh_main(self, pane, storepath):
    #pane.dataController("""
    #    var cssbag =  genro.dom.styleSheetsToBag();
    #    genro.setData('gnr.stylesheet',cssbag);
    #    cssbag.setBackRef();
    #    cssbag.subscribe('styleTrigger',{'any':dojo.hitch(genro.dom, "styleTrigger")});
    #""",_onStart=True)
        pane.dataController("""var kw = $2.kw;
                            if(kw.reason){
                                genro.dom.styleSheetBagSetter($1.getValue(),kw.reason.attr);                                   
                            }
                            """, _fired="^%s" % storepath)

        pane.dataController("""
           var cssbag =  genro.dom.styleSheetsToBag();
           genro.setData('gnr.stylesheet',cssbag);
           var storeTrigger = function(){
               console.log(arguments);
           };
           cssbag.setBackRef();
           cssbag.subscribe('styleTrigger',{'any':dojo.hitch(genro.dom, "styleTrigger")});
           store.subscribe('storeTrigger',{'any':storeTrigger});
           """, _onStart=True, store='=%s' % storepath)
        self._cssh_colorPaletteMenu(pane)

    def _cssh_colorPaletteMenu(self, pane):
        menuitem = pane.div().menu(modifiers='*', id='cssh_colorPaletteMenu', _class='colorPaletteMenu',
                                   connect_onOpen="""
                                            var connectedNode = this.widget.originalContextTarget.sourceNode;
                                            var paletteNode = genro.nodeById('cssh_colorPalette');
                                            objectExtract(paletteNode.attr,'_set_*'); 
                                            for (var attr in connectedNode.attr){
                                                if(stringStartsWith(attr,'_set_')){
                                                    paletteNode.attr[attr] = connectedNode.attr[attr];
                                                }
                                            }
                                            var path = connectedNode.absDatapath();
                                            SET _temp.csshcolor=path;
                                             """,
                                   ).menuItem(datapath='^_temp.csshcolor')
        menuitem.colorPalette(value='^.color', nodeId='cssh_colorPalette',
                              connect_ondblclick='dijit.byId("cssh_colorPaletteMenu").onCancel();')

    def cssh_colorSample(self, parent, selector=None, cssproperty=None, **kwargs):
        kwargs['width'] = '12px'
        if 'value' in kwargs:
            kwargs['width'] = '8em'
        kwargs['_set_%s' % cssproperty] = '%s:"#"' % selector
        parent.div(border='1px solid black',
                   height='12px', connectedMenu='cssh_colorPaletteMenu', **kwargs)
