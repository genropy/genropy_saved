# -*- coding: UTF-8 -*-

# test_th.py
# Created by Niso on 2011-05-10.
# Copyright (c) 2011 Softwell. All rights reserved.

class GnrCustomWebPage(object):
    py_requires = """th/th:TableHandler"""
    
    def main_(self,root,**kwargs):
        root.attributes.update(datapath='test')
        #th = root.stackTableHandler(table='agenda.staff',virtualStore=True)
        #th = root.dialogTableHandler(table='agenda.staff',virtualStore=True,
        #                             dialog_width='300px',dialog_height='200px')
        th = root.paletteTableHandler(table='agenda.staff',virtualStore=True,
                                      formResource='pierino:Paperino',
                                      viewResource=':NisoView', # = viewResource='th_staff:NisoView'
                                      #viewResource='pierino',
                                      palette_width='300px',palette_height='200px')
                                      
    def main(self,root,**kwargs):
        root.attributes.update(datapath='test')
        th = root.stackTableHandler(table='agenda.azienda',formResource=':FormFull',virtualStore=True)
        