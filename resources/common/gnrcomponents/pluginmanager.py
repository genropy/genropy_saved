# -*- coding: UTF-8 -*-

# untitled.py
# Created by Francesco Porcari on 2011-02-25.
# Copyright (c) 2011 Softwell. All rights reserved.

from gnr.web.gnrbaseclasses import BaseComponent
from gnr.web.gnrwebstruct import struct_method

class PluggedPageManager(BaseComponent):
    
    @struct_method
    def ppm_pluginTabs(self,parent,plugins=None,startPos=None,datapathTemplate=None,remoteTemplate=None, **kwargs):
        # print 'plugins'
        # print plugins
        parent.dataController("""
            var sourceNode = this.getParentNode();
            plugins = plugins? plugins.toLowerCase():'';
            var tablist = plugins.split(',');
            var content = sourceNode.getValue('static');
            var k = startPos;
            var currNode,p;
            dojo.forEach(tablist,function(plugin){
                if(!content.getItem(plugin)){
                var dpath = datapathTemplate?datapathTemplate.replace('$',plugin):null;
                p = sourceNode._('BorderContainer',plugin,{'title':plugin.toUpperCase(),
                                                        nodeId:plugin+'_plugin_tab',
                                                    _plugin:true,pageName:'plugin_'+plugin,
                                                    datapath:dpath},
                            {'_position':k});
                p._('ContentPane',{region:'center',remote:'ppm_pluginTab',
                                    remote_handlerName:remoteTemplate.replace('$',plugin),
                                    remote__onRemote:function(){
                                        sourceNode.setRelativeData('#FORM.plugin.'+plugin+'.built',true,null,true);
                                    }});
                }else{
                    currNode = content.getNode('#'+k);
                    while(currNode &&(currNode.label!=plugin)&&(currNode.attr._plugin==true)){
                        content.popNode('#'+k);
                        currNode = content.getNode('#'+k);
                    }
                }
                k++;
            });
            while(k<content.len()){
            if(content.getNode('#'+k).attr._plugin){
                content.popNode('#'+k);
            }else{
                k++;
            }
            sourceNode.widget.layout();
    }   
    """,plugins=plugins,datapathTemplate=datapathTemplate,startPos=startPos or len(parent),
        remoteTemplate=remoteTemplate)
    
    def remote_ppm_pluginTab(self,pane,handlerName=None,**kwargs):
        handler = getattr(self, handlerName)
        handler(pane.borderContainer(),**kwargs)


    def ppm_callPluginRecordHooks(self,hook,*args,**kwargs):
        methods = [k for k in dir(self) if k.endswith('_%s' %hook)]
        for m in methods:
            if hasattr(self,m):
                getattr(self,m)(*args,**kwargs)
        