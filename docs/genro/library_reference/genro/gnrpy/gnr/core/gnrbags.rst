.. _genro_library_gnrbags:

===========================================================
:mod:`gnr.core.gnrbag` and related stuff -- Bags and Struct
===========================================================

	.. note::

		It is better to have 100 functions operate on one data structure
		than 10 functions on 10 data structures.
		– Alan J. Perlis, Epigrams on Programming

* Index of ``gnr.core.gnrbag`` methods:
	
	Main classes:
	
	* :ref:`gnrbags_bag`
	* :ref:`gnrbags_bagnode`
	
	Other classes:
	
	* :ref:`gnrbags_bagcbresolver`
	* :ref:`gnrbags_bagformula`
	* :ref:`gnrbags_bagresolver`
	* :ref:`gnrbags_bagvalidationlist`
	* :ref:`gnrbags_directoryresolver`
	* :ref:`gnrbags_urlresolver`
	
* :ref:`gnrbags_classes`

.. _gnrbags_bag:

:class:`Bag`
============

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

:class:`BagNode`
================

	.. module:: gnr.core.gnrbag.BagNode

	The Genro ``BagNode`` has a relevant number of methods. They are listed here in alphabetical order.

	======================== ======================== =============================
	:meth:`addValidator`     :meth:`getValue`         :meth:`setStaticValue`       
	:meth:`delAttr`          :meth:`hasAttr`          :meth:`setValue`             
	:meth:`getAttr`          :meth:`resolver`         :meth:`staticvalue`          
	:meth:`getLabel`         :meth:`setAttr`          :meth:`subscribe`            
	:meth:`getStaticValue`   :meth:`setLabel`         :meth:`value`                
	======================== ======================== =============================

.. _gnrbags_bagcbresolver:

:class:`BagCbResolver`
======================

	.. module:: gnr.core.gnrbag.BagCbResolver

	:meth:`load`

.. _gnrbags_bagformula:

:class:`BagFormula`
===================

	.. module:: gnr.core.gnrbag.BagFormula

	* :meth:`init`
	* :meth:`load`

.. _gnrbags_bagresolver:

:class:`BagResolver`
====================

	.. module:: gnr.core.gnrbag.BagResolver

	===================== =================== ============================
	:meth:`digest`        :meth:`iterkeys`    :meth:`resolverDescription` 
	:meth:`getAttributes` :meth:`itervalues`  :meth:`resolverSerialize`   
	:meth:`init`          :meth:`keys`        :meth:`setAttributes`       
	:meth:`items`         :meth:`load`        :meth:`sum`                 
	:meth:`iteritems`     :meth:`reset`       :meth:`values`              
	===================== =================== ============================

.. _gnrbags_bagvalidationlist:

:class:`BagValidationList`
====================

	.. module:: gnr.core.gnrbag.BagValidationList

	====================== ==========================
	:meth:`add`            :meth:`validate_case`     
	:meth:`coerceFromText` :meth:`validate_db`       
	:meth:`defaultExt`     :meth:`validate_hostaddr` 
	:meth:`getdata`        :meth:`validate_inList`   
	:meth:`remove`         :meth:`validate_length`   
	====================== ==========================

.. _gnrbags_directoryresolver:

:class:`DirectoryResolver`
===================

	.. module:: gnr.core.gnrbag.DirectoryResolver

	* :meth:`load`
	* :meth:`makeLabel`
	* :meth:`processor_default`
	* :meth:`processor_directory`
	* :meth:`processor_html`
	* :meth:`processor_txt`
	* :meth:`processor_xml`

.. _gnrbags_urlresolver:

:class:`UrlResolver`
======================

	.. module:: gnr.core.gnrbag.UrlResolver

	:meth:`load`

.. _gnrbags_classes:

:mod:`gnr.core.gnrbag` - The complete reference list
====================================================

.. automodule:: gnr.core.gnrbag
	:members:
	:synopsis: the foundamental data structure in GenroPy.