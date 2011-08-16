# -*- coding: UTF-8 -*-
 
# validations.py
# Created by Filippo Astolfi on 2011-05-10.
# Copyright (c) 2011 Softwell. All rights reserved.
 
class GnrCustomWebPage(object):
    py_requires = """th/th:TableHandler"""
    
    def main(self,root,**kwargs):
        root.attributes.update(datapath='test')
        bc = root.stackTableHandler(table='agenda.staff',virtualStore=True,
                                    #viewResource='th_staff:View',
                                    formResource=':FormValidations')