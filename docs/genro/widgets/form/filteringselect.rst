=================
 FilteringSelect
=================

.. currentmodule:: form

.. class:: filteringSelect -  Genropy filteringSelect

	- :ref:`main-definition`
	
	- :ref:`where-is-it-?`
	
	- :ref:`A-brief-description`
	
	- :ref:`some-examples`
	
	- :ref:`main-attributes`
	
	- :ref:`other-features`
	
		- ???:ref:`first-reference`
		- ???:ref:`second-reference`

	.. _main-definition:

??? CONTINUARE DA QUI! ???

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

Definition
==========
		
	Here we report ???'s definition::
		
		def formbuilder(self, cols=1, dbtable=None, tblclass='formbuilder',
	                    lblclass='gnrfieldlabel', lblpos='L', _class='', fieldclass='gnrfield',
	                    lblalign=None, lblvalign='middle',
	                    fldalign=None, fldvalign='middle', disabled=False,
	                    rowdatapath=None, head_rows=None, **kwargs):

	.. _where-is-it-?:

Where
=====

	You can find ??? in *genro/gnrpy/???*

	.. _A-brief-description:

Description
===========

	???

	.. _some-examples:

Examples
========

	Let's see a code example::
	
		class GnrCustomWebPage(object):
			def main(self,root,**kwargs):
				fb=pane.formbuilder(datapath='test1',cols=2)
				???

	Let's see its graphical result:

	.. figure:: ???.png

	.. _main-attributes:

Attributes
==========

	+--------------------+-------------------------------------------------+--------------------------+
	|   Attribute        |          Description                            |   Default                |
	+====================+=================================================+==========================+
	| ``datapath``       | Set path for data.                              |  ``None``                |
	|                    | For more details, see :doc:`/common/datapath`   |                          |
	+--------------------+-------------------------------------------------+--------------------------+
	| ``disabled``       | If True, user can't act on the ???.             |  ``False``               |
	|                    | For more details, see :doc:`/common/disabled`   |                          |
	+--------------------+-------------------------------------------------+--------------------------+
	| ``hidden``         | Hide the ???.                                   |  ``False``               |
	|                    | See :doc:`/common/hidden`                       |                          |
	+--------------------+-------------------------------------------------+--------------------------+
	| ``label``          | Set ??? label.                                  |  ``None``                |
	|                    | For more details, see :doc:`/common/label`      |                          |
	+--------------------+-------------------------------------------------+--------------------------+
	| ``value``          | Set a path for ???'s values.                    |  ``None``                |
	|                    | For more details, see :doc:`/common/datastore`  |                          |
	+--------------------+-------------------------------------------------+--------------------------+

	.. _other-features:

Other features:
==============

	.. _first-reference:
	
??? Title first reference
=======================
	
	???
	
	.. _second-reference:
	
??? Title second reference
=======================
	
	???
