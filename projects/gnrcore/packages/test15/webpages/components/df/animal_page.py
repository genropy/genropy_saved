# -*- coding: UTF-8 -*-

# hdevice.py
# Created by Fabio Cristofanelli on 2011-03-25.
# Copyright (c) 2011 MedMedia snc. All rights reserved.

class GnrCustomWebPage(object):
    py_requires="""public:Public,gnrcomponents/htablehandler:HTableHandler,
                  gnrcomponents/dynamicform/dynamicform:DynamicForm""" 
    def windowTitle(self):
        return 'Animals'

    def main(self, root, **kwargs):
        frame = root.rootBorderContainer(title='Animals')
        #frame.paletteTemplateEditor(maintable='^main.edit.record.dbtable')
        self.htableHandler(frame, table='test15.animal', nodeId='animal', datapath='main')
 
        
    def tipo_impianto_form(self,parentBC,table=None,disabled=None,**kwargs):
        bc = parentBC.borderContainer(**kwargs)
        top = bc.contentPane(region='top',margin='2px',height='150px')
        fb = top.formbuilder(cols=2, border_spacing='4px',disabled=disabled, table=table)
        fb.field('name')
        fb.field('age')
        fb.field('species_id',tag='hdbselect')
        fb.field('child_code',lbl='Codice')
        fb.field('description',lbl='Descrizione')
        bc.contentPane(region='center').dynamicFieldsPane(df_table='test15.species',df_pkey='^#FORM.record.species_id',datapath='#FORM.record.abilities')
