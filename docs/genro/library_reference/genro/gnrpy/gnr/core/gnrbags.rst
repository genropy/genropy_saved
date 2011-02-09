.. _genro_library_gnrbags:

===========================================================
:mod:`gnr.core.gnrbag` and related stuff -- Bags and Struct
===========================================================

	.. note::

		It is better to have 100 functions operate on one data structure
		than 10 functions on 10 data structures.
		– Alan J. Perlis, Epigrams on Programming
	
	* Indexes:
	
		* :ref:`gnrbags_bag`
		* :ref:`gnrbags_bagnode`
		
	* :ref:`gnrbags_classes`

.. _gnrbags_bag:

the :class:`Bag` methods
========================

	.. module:: gnr.core.gnrbag.Bag

	The Genro :ref:`genro_bag_intro` has a consistent number of methods. They are listed here in alphabetical order.

	======================== ======================== ============================= =====================
	:meth:`addItem`          :meth:`fillFrom`         :meth:`has_key`               :meth:`setItem`      
	:meth:`addValidator`     :meth:`formula`          :meth:`items`                 :meth:`setResolver`  
	:meth:`asDict`           :meth:`fromXml`          :meth:`keys`                  :meth:`setdefault`   
	:meth:`asString`         :meth:`getAttr`          :meth:`makePicklable`         :meth:`sort`         
	:meth:`child`            :meth:`getDeepestNode`   :meth:`merge`                 :meth:`subscribe`    
	:meth:`clear`            :meth:`getDeepestNode_`  :meth:`nodes`                 :meth:`toTree`       
	:meth:`clearBackRef`     :meth:`getFormula`       :meth:`pickle`                :meth:`toXml`        
	:meth:`copy`             :meth:`getIndex`         :meth:`pop`                   :meth:`unpickle`     
	:meth:`deepcopy`         :meth:`getIndexList`     :meth:`removeValidator`       :meth:`unsubscribe`  
	:meth:`defineFormula`    :meth:`getItem`          :meth:`restoreFromPicklable`  :meth:`update`       
	:meth:`defineSymbol`     :meth:`getNode`          :meth:`setAttr`               :meth:`values`       
	:meth:`delItem`          :meth:`getNodeByAttr`    :meth:`setBackRef`            :meth:`walk`         
	:meth:`delParentRef`     :meth:`getNodes`         :meth:`setCallBackItem`                            
	:meth:`digest`           :meth:`getResolver`      :meth:`setCallable`                                
	======================== ======================== ============================= =====================

.. _gnrbags_bagnode:

the :class:`BagNode` methods
============================

	.. module:: gnr.core.gnrbag.BagNode

	The Genro ``BagNode`` has a relevant number of methods. They are listed here in alphabetical order.

	======================== ======================== =============================
	:meth:`addValidator`     :meth:`getValue`         :meth:`setStaticValue`       
	:meth:`delAttr`          :meth:`hasAttr`          :meth:`setValue`             
	:meth:`getAttr`          :meth:`resolver`         :meth:`staticvalue`          
	:meth:`getLabel`         :meth:`setAttr`          :meth:`subscribe`            
	:meth:`getStaticValue`   :meth:`setLabel`         :meth:`value`                
	======================== ======================== =============================

.. _gnrbags_classes:

The :mod:`gnr.core.gnrbag` classes
==================================

.. automodule:: gnr.core.gnrbag
	:members:
	:synopsis: the foundamental data structure in GenroPy.