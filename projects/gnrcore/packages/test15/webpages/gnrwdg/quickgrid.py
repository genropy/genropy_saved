# -*- coding: UTF-8 -*-

# bageditor.py
# Created by Francesco Porcari on 2011-01-10.
# Copyright (c) 2011 Softwell. All rights reserved.

"""bageditor"""
from gnr.core.gnrbag import Bag
from gnr.core.gnrdecorator import public_method
import psutil

class GnrCustomWebPage(object):
    py_requires="gnrcomponents/testhandler:TestHandlerFull,gnrcomponents/framegrid:FrameGrid"
    css_requires='public'
    def test_1_columns_editable(self,pane):
        t = pane.table().tbody()
        r = t.tr()
        self.quickGridEditable(r.td(border='1px solid silver',padding='4px'),pos='TL')
       #self.quickGridEditable(r.td(border='1px solid silver',padding='4px'),pos='TR')
       #r = t.tr()
       #self.quickGridEditable(r.td(border='1px solid silver',padding='4px'),pos='BL')
       #self.quickGridEditable(r.td(border='1px solid silver',padding='4px'),pos='BR')


    def quickGridEditable(self,pane,pos=None):
        box = pane.div(datapath='.%s' %pos)
        b = Bag()
        pane.data('.griddata',b)
        fb = box.formbuilder()
        fb.textBox('^.def_location',lbl='Default location')
        fb.checkbox('^.pippo',label='pippo')
        grid = box.quickGrid(value='^.griddata',
                        columns='^.columns',
                        default_location='=.def_location',
                        height='150px',width='400px' ,border='1px solid silver'
                        )
        grid.tools('addrow,delrow,duprow,export',position=pos)
        grid.column('location',name='Location',width='15em',edit=dict(tag='dbselect',dbtable='glbl.provincia'))
        grid.column('name',name='Name',width='15em',edit=True)
        grid.column('is_ok',name='Ok',dtype='B',edit=True)
          


    def test_2_syntax(self,pane):
        """basic"""
        bc = pane.borderContainer(height='500px')
        fb = bc.contentPane(region='top').formbuilder(cols=2,border_spacing='3px')
        fb.dbselect(value='^.provincia',dbtable='glbl.provincia',lbl='provincia')
        fb.textBox('^.fields',lbl='Fields')
        fb.dataRpc('.data',self.bagComuni,provincia='^.provincia',_if='provincia',_else='null')

        grid = bc.contentPane(region='center').quickGrid(value='^.data',height='300px',fields='^.fields')
        grid.column('denominazione',color='red',width='40em',name='Den',edit=True)
        grid.tools('export',position='TR')
       #grid.column('denominazione')
       #grid.column('sigla')

    @public_method
    def bagComuni(self,provincia=None):
        f = self.db.table('glbl.comune').query(where='$sigla_provincia=:pr',pr=provincia).fetch()
        result = Bag()
        for r in f:
            r = dict(r)
            r['is_ok'] = None
            result[r['id']] = Bag(r)
        return result


    def test_3_syntax(self,pane):
        """basic"""
        bc = pane.borderContainer(height='500px')
        fb = bc.contentPane(region='top').formbuilder(cols=2,border_spacing='3px')
        fb.dbselect(value='^.provincia',dbtable='glbl.provincia',lbl='provincia')
        fb.textBox('^.fields',lbl='Fields')
        fb.dataRpc('.data',self.bagComuniAttr,provincia='^.provincia',_if='provincia',_else='null')

        grid = bc.contentPane(region='center').quickGrid(value='^.data',height='300px',fields='^.fields',
                                                        datamode='attr')
        grid.column('denominazione',color='red',width='40em',name='Den',edit=True)
        grid.tools('export',position='TR')
       #grid.column('denominazione')
       #grid.column('sigla')

    @public_method
    def bagComuniAttr(self,provincia=None):
        return self.db.table('glbl.comune').query(where='$sigla_provincia=:pr',pr=provincia).selection().output('selection')
 

        # columns = None => autocalcola
        # columns = 'pippo,pluto' ==> autocalcola solo pippo e pluto
        # column_pippo = dict(), column_pluto = dict()
        # grid.column('pippo') grid.column('pluto')
        # columns = '^.columns'
    
    
        #grid.tools('addrow,delrow',position='TR')
    

    def test_4_cpu(self,pane,**kwargs):
        pane=pane.div(margin='15px',datapath='.cpuTimes',height='500px',width='500px')
        pane.quickGrid(value='^.data',
                       border='1px solid silver',
                              font_family='courier',
                              font_weight='bold',
                              height='auto',width='auto'
                              )
        
        pane.dataRpc('.data', self.getCpuTimes,
                     #_timing=2,
                     _onStart=True)
    @public_method
    def getCpuTimes(self):
        result=Bag()
        columns=['user','nice','system','idle']
        for j, core in enumerate(psutil.cpu_times(True)):
            row = Bag()
            row['core']=j+1
            for k in columns:
                row.setItem(k, getattr(core,k))
            result.setItem('r_%i'%j, row)
        return result

