#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#
#  index.py


""" index.py """
from gnr.core.gnrdecorator import public_method
# --------------------------- GnrWebPage subclass ---------------------------
class GnrCustomWebPage(object):
    dojo_source=True
    py_requires = """public:Public,th/th:TableHandler"""
    auth_page='admin,superadmin,_DEV_'
    pageOptions={'liveUpdate':True,'userConfig':False}

    def main(self, root,**kwargs):
        frame = root.rootBorderContainer(datapath='main',design='sidebar',title='!![it]Checklist viewer') 
        frame.contentPane(region='center').plainTableHandler(table='adm.install_checklist',
                                                            viewResource='ViewChecklist',
                                                            view_store_onStart=True)
