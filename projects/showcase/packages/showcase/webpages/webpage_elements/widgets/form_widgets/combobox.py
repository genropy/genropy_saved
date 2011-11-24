# -*- coding: UTF-8 -*-
"""Combobox"""

from gnr.core.gnrbag import Bag

class GnrCustomWebPage(object):
    py_requires = "gnrcomponents/testhandler:TestHandlerFull"
    
    def test_1_values(self, pane):
        """Combobox filled through "values" attribute"""
        pane.combobox(value='^.record.values', values='Football,Golf,Karate',
                      lbl='loaded through values')

    def test_2_bag(self, pane):
        """Combobox filled through a Bag"""
        pane.data('.values.sport', self.sports(), id='.pkey', caption='.Description')
        pane.combobox(value='^.record', storepath='.values.sport')
        
    def sports(self, **kwargs):
        mytable = Bag()
        mytable['r1.pkey'] = 'SC'
        mytable['r1.Description'] = 'Soccer'
        mytable['r2.pkey'] = 'BK'
        mytable['r2.Description'] = 'Basket'
        mytable['r3.pkey'] = 'TE'
        mytable['r3.Description'] = 'Tennis'
        mytable['r4.pkey'] = 'HK'
        mytable['r4.Description'] = 'Hockey'
        mytable['r5.pkey'] = 'BB'
        mytable['r5.Description'] = 'Baseball'
        mytable['r6.pkey'] = 'SB'
        mytable['r6.Description'] = 'Snowboard'
        return mytable