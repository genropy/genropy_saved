# -*- coding: UTF-8 -*-

# frameindex.py
# Created by Francesco Porcari on 2011-04-06.
# Copyright (c) 2011 Softwell. All rights reserved.

from gnr.web.gnrwebpage import BaseComponent

class Mixin(BaseComponent):
    py_requires='public:Public,foundation/menu:MenuIframes'
    plugin_list = 'iframemenu_plugin,batch_monitor,chat_plugin'
    index_url = None
    showTabs = False
    
    def rootWidget(self, root, **kwargs):
        tag = 'TabContainer' if self.showTabs else 'StackContainer'
        return root.child(tag=tag,selectedPage='^selectedFrame',nodeId='center_stack',region='center')
    
    def main(self, root, **kwargs):
        if self.index_url:
            root.contentPane(pageName='index',title='Index').iframe(height='100%', width='100%', src=self.index_url, border='0px')
        root.dataController("""
            var sc = genro.nodeById("center_stack");
            var page = sc.getValue().getItem(name);
            var url;
            if(!page){
                 page = sc._('ContentPane',name,{pageName:name,title:label,overflow:'hidden',nodeId:name});
                 url = file;
                 if(table){
                    url = '/adm/th/thrunner/'+table.replace('.','/');
                 }
                 else{
                    url = file;
                    if(url.indexOf('?')>0){
                        url+='&&inframe=true'
                    }else{
                        url+='?inframe=true'
                    }
                 }
             }
            SET selectedFrame = name;
            if(url){
                setTimeout(function(){page._('iframe',{'height':'100%','width':'100%','border':0,src:url});},1);
            }
        """,subscribe__menutree__selected=True)

    