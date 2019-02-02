# -*- coding: utf-8 -*-

# palette_manager.py
# Created by Francesco Porcari on 2010-12-27.
# Copyright (c) 2010 Softwell. All rights reserved.
 
"""Test Protovis"""

   
from builtins import range
from builtins import object
from gnr.core.gnrbag import Bag
from random import randint
from gnr.core.gnrdecorator import public_method
from datetime import datetime
from dateutil import rrule
from collections import OrderedDict


class GnrCustomWebPage(object):
    py_requires="gnrcomponents/testhandler:TestHandlerFull"
    
    def test_1_simple(self, pane):
        pane.dygraph(data=[
                [1,10,100],
                [2,20,80],
                [3,50,60],
                [4,70,80]
              ],options={'labels': [ "x", "A", "B" ]},
              height='300px',width='600px',border='1px solid silver')

    def datastruct(self,struct):
        r = struct.view().rows()
        r.cell('c_0',name='Prog',dtype='L')
        r.cell('c_1',name='Foo',dtype='L')
        r.cell('c_2',name='Bar',dtype='L')


    def datastruct_dt(self,struct):
        r = struct.view().rows()
        r.cell('c_0',name='TS',dtype='DH',width='10em')
        r.cell('c_1',name='Foo',dtype='L')
        r.cell('c_2',name='Bar',dtype='L')

    def test_2_bagData(self, pane):
        pane.data('.data',self.getTestData(n=10,series=[(1,100),(1,100)]))
        pane.data('.options.labels',['x','Foo','Bar'])
        bc = pane.borderContainer(height='600px',width='800px',_anchor=True)
        bc.contentPane(region='left',width='300px').frameGrid(storepath='#ANCHOR.data',
                                                            struct=self.datastruct,
                                                            datapath='.prevgrid')
        bc.contentPane(region='center').dygraph(data='^.data',options='^.options',
                    columns='c_0,c_1,c_2',
                    height='300px',width='450px',border='1px solid silver')


    def test_3_bagData(self, pane):
        pane.data('.data',self.getTestData(dtstart=datetime.now(),interval=15,count=50,
                                            series=[(1,100),(1,100)]))
        pane.data('.options.labels',['x','Foo','Bar'])
        pane.data('.options.hideOverlayOnMouseOut',False)
        bc = pane.borderContainer(height='600px',width='800px',_anchor=True)
        bc.contentPane(region='left',width='300px',splitter=True).frameGrid(storepath='#ANCHOR.data',
                                                            struct=self.datastruct_dt,
                                                            datapath='.prevgrid')
        bc.contentPane(region='center').dygraph(data='^.data',options='^.options',
                    columns='c_0,c_1,c_2',
                     height='300px',width='450px')



    def test_4_bagDataValue(self, pane):
        pane.data('.data',self.getTestData(n=10,series=[(1,100),(1,100)],datamode='value'))
        pane.data('.options.labels',['x','Foo','Bar'])
        bc = pane.borderContainer(height='600px',width='800px',_anchor=True)
        tc = bc.tabContainer(region='left',width='300px')
        grid = tc.contentPane(title='Data').quickGrid(value='^.data')
        grid.tools('delrow,addrow')
        grid.column('c_0',edit=True,name='N',dtype='L')
        grid.column('c_1',edit=True,name='Foo',dtype='L')
        grid.column('c_2',edit=True,name='Bar',dtype='L')
        bc.contentPane(region='center',overflow='hidden').dygraph(data='^.data',options='^.options',
                    columns='c_0,c_1,c_2',
                    height='300px',width='450px',
                    border='1px solid silver',
                    detachable=True)
        #grid = tc.contentPane(title='Labels').multiValueEditor(value='^.options.labels')
        tc.contentPane(title='Options').multiValueEditor(value='^.options',nodeId='optionseditor')


    @public_method
    def getTestData(self,n=None,count=None,interval=None,dtstart=None,series=None,datamode=None):
        result = Bag()
        if n:
            g = range(1,n)
        else:
            g = rrule.rrule(rrule.MINUTELY,count=count,interval=interval,dtstart=dtstart)
        j = 0
        for i in g:
            attr = OrderedDict(c_0=i)
            for k,s in enumerate(series):
                attr['c_%s' %(k+1)] = randint(*s)
            if datamode=='value':
                result.setItem('r_%s' %j,Bag(attr))
            else:
                result.setItem('r_%s' %j,None,attr)
            j+=1
        return result
        