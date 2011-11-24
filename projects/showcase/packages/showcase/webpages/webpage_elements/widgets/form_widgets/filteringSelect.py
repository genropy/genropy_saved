# -*- coding: UTF-8 -*-
"""filteringSelect"""

from gnr.core.gnrbag import Bag

class GnrCustomWebPage(object):
    py_requires = "gnrcomponents/testhandler:TestHandlerFull"
    
    def test_1_values(self, pane):
        """values example"""
        fb = pane.formbuilder(cols=2)
        fb.filteringSelect(value='^.sport',
                           values="""SC:Soccer,BK:Basket,HK:Hockey,
                                     TE:Tennis,BB:Baseball,SB:Snowboard'""")
        fb.div('Values loaded through \"values\" attribute')
        
    def test_2_bag(self, pane):
        """Bag example"""
        fb = pane.formbuilder(cols=2)
        pane.data('.bag', self.sports(), id='.pkey', caption='.Description')
        fb.filteringSelect(value='^.value_bag', storepath='.bag')
        fb.div('Values loaded through a Bag')
        
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