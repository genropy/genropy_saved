# -*- coding: UTF-8 -*-

# frameindex.py
# Created by Francesco Porcari on 2011-04-06.
# Copyright (c) 2011 Softwell. All rights reserved.

from gnr.web.gnrwebpage import BaseComponent

class Mixin(BaseComponent):
    py_requires='public:Public,foundation/menu:MenuIframes'
    js_requires='frameindex'
    plugin_list = 'iframemenu_plugin,batch_monitor,chat_plugin'
    index_url = None
    showTabs = False
    
    def rootWidget(self, root, **kwargs):
        tag = 'TabContainer' if self.showTabs else 'StackContainer'
        return root.child(tag=tag,selectedPage='^selectedFrame',nodeId='center_stack',region='center')
    
    def main(self, root, **kwargs):
        page = self.pageSource()
        page.dataController("PUBLISH main_left_set_status='open';",_onStart=True)
        if self.index_url:
            root.contentPane(pageName='index',title='Index').iframe(height='100%', width='100%', src=self.index_url, border='0px')
        page.dataController("""
            frameIndex.selectIframePage(this,name,label,file,table,formResource,viewResource)
        """,subscribe__menutree__selected=True)

    