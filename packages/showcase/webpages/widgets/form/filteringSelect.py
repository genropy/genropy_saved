#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-

#  Created by Giovanni Porcari on 2007-03-24.
#  Copyright (c) 2007 Softwell. All rights reserved.

""" Filtering select """

from gnr.core.gnrbag import Bag

class GnrCustomWebPage(object):
    """ The filteringSelect is a text field who suggests to user the possible (and unique!) entries 
    of his selection.
    
    FilteringSelect's values are composed by a key and a value (like the Python dictionary's elements):
    user can chooses from values, while in database the user's choice is saved through keys.
    User can also freely type text and partially matched values will be shown in a pop-up menu below the 
    input text box.
    
    FilteringSelect widgets are dojo.data-enabled. This means rather than embedding all the OPTION tags within 
    the page, you can have dojo.data fetch them from a server-based store. The unified dojo.data architecture can get 
    its data from various places such as databases and web services.
    
    Warning: actually (13/10/2010) the filteringSelect doesn't warn user for its wrong insertion. You can
    add a warning for the user through a "validate" attribute.
    
    - filteringSelect's attributes (and default values)
        ignoreCase (True)       If True, user can write in filteringSelect ignoring case.
        values                  Contains all the entries from which users have to choose. """
    
    #   - Other forms and attributes:
    #       In this section we report forms/attributes that have been used in this example
    #       despite they didn't strictly belonging to filteringSelect.
    #       We also suggest you the file (if it has been created!) where you can find
    #       some documentation about them.
    #
    #       ## name ##      --> ## file ##
    #       Bag             --> bag.py
    #       datapath        --> datapath.py
    #       formbuilder     --> formbuilder.py
    #       value           --> datapath.py
    
    py_requires="gnrcomponents/testhandler:TestHandlerBase"
    # dojo_theme='claro'    # !! Uncomment this row for Dojo_1.5 usage
    
    def test_1_basic(self,pane):
        """Basic example"""
        pane.data('bag',self.sports(),id='.pkey',caption='.Description')
        fb = pane.formbuilder(datapath='test_1.record',cols=2)
        fb.filteringSelect(value='^.loaded_values',
                           values='SC:Soccer,BK:Basket,HK:Hockey,TE:Tennis,BB:Baseball,SB:Snowboard')
        fb.div("""Values loaded through "values" attribute.""",
                font_size='.9em',text_align='justify')
        
    def test_2_bag(self,pane):
        """Bag example"""
        fb = pane.formbuilder(datapath='test_2.record',cols=2)
        fb.filteringSelect(value='^.bag_values',storepath='bag')
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