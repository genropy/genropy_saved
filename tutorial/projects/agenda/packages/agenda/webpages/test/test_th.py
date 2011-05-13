# -*- coding: UTF-8 -*-
 
# test_th.py
# Created by Filippo Astolfi on 2011-05-10.
# Copyright (c) 2011 Softwell. All rights reserved.
 
class GnrCustomWebPage(object):
    py_requires = """th/th:TableHandler"""
    
    def main(self,root,**kwargs):
        root.attributes.update(datapath='test')
        #th = root.stackTableHandler(table='agenda.staff',virtualStore=True)
        #th = root.dialogTableHandler(table='agenda.staff',virtualStore=True,
        #                             dialog_width='600px',dialog_height='400px')
        th = root.paletteTableHandler(table='agenda.staff',virtualStore=True,
                                      formResource='pierino:Paperino',
                                      #viewResource=':NisoView', # = viewResource='th_staff:NisoView'
                                      #viewResource='pierino',
                                      palette_width='600px',palette_height='400px')
        #bc = root.borderTableHandler(table='agenda.staff',virtualStore=True)
        #pc = root.plainTableHandler(table='agenda.staff',virtualStore=True)
        
    def main_(self,root,**kwargs):
        root.attributes.update(datapath='test')
        th = root.stackTableHandler(table='agenda.azienda',formResource=':FormFull',virtualStore=True)