# -*- coding: UTF-8 -*-

# filteringSelect.py
# Created by Niso on 2010-09-13.
# Copyright (c) 2010 Softwell. All rights reserved.

""" Filtering select """

from gnr.core.gnrbag import Bag

class GnrCustomWebPage(object):
    py_requires="gnrcomponents/testhandler:TestHandlerFull"
    # dojo_theme='claro'    # !! Uncomment this row for Dojo_1.5 usage
    
    """
    =================
     filteringSelect
    =================

    .. currentmodule:: form

    .. class:: filteringSelect -  Genropy filteringSelect

    	The filteringSelect is a text field who suggests to user the possible (and unique!) entries of his selection.

    	FilteringSelect's values are composed by a key and a value (like the Python dictionary's elements): user can chooses from values, while in database the user's choice is saved through keys. User can also freely type text and partially matched values will be shown in a pop-up menu below the input text box.

    		+----------------+----------------------------------------------------------+-------------+
    		|   Attribute    |          Description                                     |   Default   |
    		+================+==========================================================+=============+
    		| ``ignoreCase`` | If True, user can write in filteringSelect ignoring case |  ``True``   |
    		+----------------+----------------------------------------------------------+-------------+
    		| ``values``     | Contains all the entries from which users have to choose |  ``None``   |
    		+----------------+----------------------------------------------------------+-------------+

    	The main two modes to fill a filteringSelect are:

    	    - through a bag

    	        Example::

    	            def main(self,root,**kwargs):
    	                fb = root.formbuilder(datapath='test2',cols=2)
    	                fb.filteringSelect(value='^.bag',storepath='bag')

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

    	    See "datapath" for more details.

    	    - through the "values" attributes

    	        Example::

    	            def main(self,root,**kwargs):
    	                pane.filteringSelect(value='^sports',
    	                                     values='SC:Soccer,BK:Basket,HK:Hockey,
    	                                     TE:Tennis,BB:Baseball,SB:Snowboard')

    	Pay attention not to confuse the "value" attribute with the "values" attribute: "value" is used to allocate user data in a well determined datapath, while "values" is used to fill the filteringSelect.

    	Warning: unlike Dojo, actually filteringSelect doesn't warn user for its wrong insertion. You can add a warning for the user through a "validate" attribute.
    
    """
    
    #   - Other forms and attributes:
    #       In this section we report forms/attributes that have been used in this example
    #       despite they didn't strictly belonging to filteringSelect.
    #       We also suggest you the file (if it has been created!) where you can find
    #       some documentation about them.
    #
    #       ## name ##      --> ## file ##
    #       Bag             --> bag.py
    #       formbuilder     --> formbuilder.py
    #       value           --> datapath.py
    
    def test_1_basic(self,pane):
        """Basic example"""
        pane.data('bag',self.sports(),id='.pkey',caption='.Description')
        fb = pane.formbuilder(datapath='test1',cols=2)
        fb.filteringSelect(value='^.values',
                           values='SC:Soccer,BK:Basket,HK:Hockey,TE:Tennis,BB:Baseball,SB:Snowboard')
        fb.div("""Values loaded through "values" attribute.""",
                font_size='.9em',text_align='justify')
        
    def test_2_bag(self,pane):
        """Bag example"""
        fb = pane.formbuilder(datapath='test2',cols=2)
        fb.filteringSelect(value='^.bag',storepath='bag')
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