# -*- coding: UTF-8 -*-

# bageditor.py
# Created by Francesco Porcari on 2011-01-10.
# Copyright (c) 2011 Softwell. All rights reserved.

"""bageditor"""
from gnr.core.gnrbag import Bag
from gnr.core.gnrdecorator import public_method

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
        box.formbuilder().textBox('^.def_location',lbl='Default location')
        grid = box.quickGrid(value='^.griddata',
                        columns='^.columns',
                        default_location='=.def_location',
                        height='150px',width='400px' ,border='1px solid silver'
                        )
        grid.tools('addrow,delrow,duprow,export',position=pos)
        grid.column('location',name='Location',width='15em',edit=dict(tag='dbselect',dbtable='glbl.provincia'))
        grid.column('name',name='Name',width='15em',edit=True)
                  


    def test_2_syntax(self,pane):
        """basic"""
        bc = pane.borderContainer(height='200px')
        fb = bc.contentPane(region='top').formbuilder(cols=2,border_spacing='3px')
        fb.dbselect(value='^.provincia',dbtable='glbl.provincia',lbl='provincia')
        fb.textBox('^.fields',lbl='Fields')
        fb.dataRpc('.data',self.bagComuni,provincia='^.provincia',_if='provincia',_else='null')

        grid = pane.quickGrid(value='^.data',height='300px',fields='^.fields')
        grid.column('denominazione',color='red',width='40em',name='Den',edit=True)
        grid.tools('export',position='TR')
       #grid.column('denominazione')
       #grid.column('sigla')

    @public_method
    def bagComuni(self,provincia=None):
        f = self.db.table('glbl.comune').query(where='$sigla_provincia=:pr',pr=provincia).fetch()
        result = Bag()
        for r in f:
            result[r['id']] = Bag(dict(r))
        return result

    
    
        # columns = None => autocalcola
        # columns = 'pippo,pluto' ==> autocalcola solo pippo e pluto
        # column_pippo = dict(), column_pluto = dict()
        # grid.column('pippo') grid.column('pluto')
        # columns = '^.columns'
    
    
        #grid.tools('addrow,delrow',position='TR')
    

        
    def _test_3_framepane_syntax(self,pane):
        """basic"""
        bc = pane.borderContainer(height='400px')
        pane=bc.framePane(region='center')
        ptop=pane.top(height='20px').slotToolbar('*,foo,egg,2')
        ptop.foo.div('pppppp')
        ptop.egg.div('pppppp')
        pbottom=pane.bottom(height='20px')
   




    @public_method
    def getCpuTimes(self):
        return self.site.getService('sysinfo').getCpuTimes()
  