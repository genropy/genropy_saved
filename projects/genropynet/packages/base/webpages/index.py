#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#
#  index.py
#
#

""" index.py """

# --------------------------- GnrWebPage subclass ---------------------------
from gnr.core.gnrdecorator import public_method
class GnrCustomWebPage(object):
    py_requires = 'frameindex,frameplugin_rubrica/frameplugin_rubrica,th/th:TableHandler'
    index_url='indexcontent.html'
    auth_workdate = 'admin'
    plugin_list = 'iframemenu_plugin,batch_monitor,chat_plugin'
    css_requires='customstyles'

    def windowTitleTemplate(self):
        return "GenroPy Developer $workdate" 

    def isDeveloper(self):
        return True
        
    def windowTitle(self):
        owner_name = self.getPreference('instance_data.owner_name',pkg='adm')
        return  owner_name or 'Indice'
        


        