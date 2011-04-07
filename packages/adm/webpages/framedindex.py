# -*- coding: UTF-8 -*-

# framedindex.py
# Created by Francesco Porcari on 2011-04-05.
# Copyright (c) 2011 Softwell. All rights reserved.

class GnrCustomWebPage(object):
    py_requires='public:Public,foundation/menu:MenuIframes'
    plugin_list = 'iframemenu_plugin,batch_monitor,chat_plugin'
         
    def rootWidget(self, root, **kwargs):
        return root.stackContainer(selectedPage='^selectedFrame',nodeId='center_stack',region='center')
    
    def main(self, root, **kwargs):
        #root = root.rootContentPane(title='ciao')
        #root.contentPane(pageName='__base__').div('test')
        root.dataController("""
            var sc = genro.nodeById("center_stack");
            var page = sc.getValue().getItem(name);
            var url;
            if(!page){
                 page = sc._('ContentPane',name,{pageName:name,title:label,overflow:'hidden',nodeId:name});
                 url = file;
                 var urlPars = {inframe:true};
                 if(table){
                    url = '/adm/th/thrunner/'+table.replace('.','/');
                    if(formName){
                        urlPars['th_formName'] = formName;
                    }
                    if(viewName){
                        urlPars['th_viewName'] = viewName;
                    }
                 }
                 url = genro.addParamsToUrl(url,urlPars);
             }
            SET selectedFrame = name;
            if(url){
                setTimeout(function(){page._('iframe',{'height':'100%','width':'100%','border':0,src:url});},1);
            }
        """,subscribe__menutree__selected=True)

    