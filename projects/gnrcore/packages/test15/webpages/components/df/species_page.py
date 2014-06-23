# -*- coding: UTF-8 -*-

# hdevice.py
# Created by Fabio Cristofanelli on 2011-03-25.
# Copyright (c) 2011 MedMedia snc. All rights reserved.

class GnrCustomWebPage(object):
    py_requires='public:Public,gnrcomponents/htablehandler:HTableHandler,gnrcomponents/dynamicform/dynamicform:DynamicForm'
        
    def windowTitle(self):
        return 'Species'

    def main(self, root, **kwargs):
        frame = root.rootBorderContainer()
        self.htableHandler(frame, table='test15.species', nodeId='species', datapath='main')
 
        
    def tipo_impianto_form(self,parentBC,table=None,disabled=None,**kwargs):
        bc = parentBC.borderContainer(**kwargs)
        top = bc.contentPane(region='top',margin='2px',height='150px')
        fb = top.formbuilder(cols=2, border_spacing='4px',disabled=disabled, table=table)
        fb.field('child_code',lbl='Code')
        fb.field('description')
        bc.contentPane(region='center').fieldsGrid(storepath='#FORM.record.abilities',margin='2px',rounded=6,border='1px solid silver')
