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
	                                 values='SC:Soccer,BK:Basket,HK:Hockey,TE:Tennis,BB:Baseball,SB:Snowboard')
	
	Pay attention not to confuse the "value" attribute with the "values" attribute: "value" is used to allocate user data in a well determined datapath, while "values" is used to fill the filteringSelect.
	
	Warning: unlike Dojo, actually filteringSelect doesn't warn user for its wrong insertion. You can add a warning for the user through a "validate" attribute.
	