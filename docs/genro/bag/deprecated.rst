	.. _genro-bag-merge:

=========
Bag merge
=========

	.. deprecated:: 0.7
	
	.. note:: This method have to be rewritten.

	.. _bag-merge:

merge
=====
	
	With the :meth:`Bag.merge` method you can merge two bags into one.
	
	It has four optional parameters:
	
	+------------------------+----------------------------------------+-----------------------------+
	|  *flag*                |  Description                           |  Default                    |
	+========================+========================================+=============================+
	| ``upd_values``         | ???                                    |  ``True``                   |
	+------------------------+----------------------------------------+-----------------------------+
	| ``add_values``         | ???                                    |  ``True``                   |
	+------------------------+----------------------------------------+-----------------------------+
	| ``upd_attr``           | ???                                    |  ``True``                   |
	+------------------------+----------------------------------------+-----------------------------+
	| ``add_attr``           | ???                                    |  ``True``                   |
	+------------------------+----------------------------------------+-----------------------------+

	>>> john_doe=Bag()
	>>> john_doe['telephones']=Bag()
	>>> john_doe['telephones.house']=55523412
	>>> other_numbers=Bag({'mobile':444334523, 'office':3320924, 'house':2929387})
	>>> other_numbers.setAttr('office',{'from': 9, 'to':17})
	>>> john_doe['telephones']=john_doe['telephones'].merge(other_numbers)
	>>> print john_doe
	0 - (Bag) telephones:
	    0 - (int) house: 2929387
	    1 - (int) mobile: 444334523
	    2 - (int) office: 3320924  <to='17' from='9'>
	>>> john_doe['credit_cards']=Bag()
	
	As you can see, since we did't set any of the flag parameters to ``False``, the :meth:`Bag.merge` method added two new values (that are "mobile", "office"), updated a value ("house") and added two attributes.
