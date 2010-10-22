# -*- coding: UTF-8 -*-

# filteringSelect.py
# Created by Filippo Astolfi on 2010-09-13.
# Copyright (c) 2010 Softwell. All rights reserved.

""" Filtering select """

from gnr.core.gnrbag import Bag

class GnrCustomWebPage(object):
    py_requires="gnrcomponents/testhandler:TestHandlerFull"
    # dojo_theme='claro'    # !! Uncomment this row for Dojo_1.5 usage
    
    # For an exhaustive documentation, please see http://docs.genropy.org/widgets/form/filteringselect.html
    
    def test_1_basic(self,pane):
        """Basic example"""
        pane.data('bag',self.sports(),id='.pkey',caption='.Description')
        fb = pane.formbuilder(datapath='test1',cols=2)
        fb.filteringSelect(value='^.values',
                           values="""SC:Soccer,BK:Basket,HK:Hockey,
                                     TE:Tennis,BB:Baseball,SB:Snowboard'""")
        fb.div("""Values loaded through "values" attribute.""",
                font_size='.9em',text_align='justify')
        
    def test_2_bag(self,pane):
        """Bag example"""
        fb = pane.formbuilder(datapath='test2',cols=2)
        fb.filteringSelect(value='^.value_bag',storepath='bag')
        fb.div("""Values loaded through a Bag.""",
                font_size='.9em',text_align='justify')
        
    def sports(self,**kwargs):
        mytable=Bag()
        mytable['r1.pkey']='SC'
        mytable['r1.Description']='Soccer'
        mytable['r2.pkey']='BK'
        mytable['r2.Description']='Basket'
        mytable['r3.pkey']='TE'
        mytable['r3.Description']='Tennis'
        mytable['r4.pkey']='HK'
        mytable['r4.Description']='Hockey'
        mytable['r5.pkey']='BB'
        mytable['r5.Description']='Baseball'
        mytable['r6.pkey']='SB'
        mytable['r6.Description']='Snowboard'
        return mytable