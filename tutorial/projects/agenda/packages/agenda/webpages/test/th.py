# -*- coding: UTF-8 -*-
 
# th.py
# Created by Filippo Astolfi on 2011-05-10.
# Copyright (c) 2011 Softwell. All rights reserved.
 
class GnrCustomWebPage(object):
    py_requires = """th/th:TableHandler"""
    
    def main(self,root,**kwargs):
        root.attributes.update(datapath='test')
        bc = root.borderTableHandler(table='agenda.contatto',virtualStore=True)
        #th = root.dialogTableHandler(table='agenda.contatto',virtualStore=True,
        #                             dialog_width='600px',dialog_height='400px')
        #th = root.paletteTableHandler(table='agenda.contatto',virtualStore=True,
        #                              #formResource='pierino:Paperino',readOnly=True,
        #                              #viewResource=':NisoView', # = viewResource='th_staff:NisoView'
        #                              #viewResource='pierino',
        #                              palette_width='600px',palette_height='400px')
        #pc = root.plainTableHandler(table='agenda.contatto',virtualStore=True)
        #th = root.stackTableHandler(table='agenda.contatto',virtualStore=True)
        
    #def main_(self,root,**kwargs):
    #    root.attributes.update(datapath='test')
    #    th = root.stackTableHandler(table='agenda.azienda',formResource=':FormFull',virtualStore=True)
    
    #    tc = root.tabContainer(margin='3px', selected='^.selected_tab')
    #    tc.contentPane(title='Companies', margin='3px').thIframe('companies')
    #    tc.contentPane(title='Staff', margin='3px').thIframe('staff')
    #    
    #def iframe_companies(self, pane, **kwargs):
    #    th = pane.dialogTableHandler(table='agenda.azienda',virtualStore=True,
    #                                 dialog_height='500px',dialog_width='700px',dialog_title='COMPANY')
    #    
    #def iframe_staff(self, pane, **kwargs):
    #    th = pane.paletteTableHandler(table='agenda.staff',virtualStore=True,
    #                                  palette_height='500px',palette_width='700px',dialog_title='STAFF')
                                     