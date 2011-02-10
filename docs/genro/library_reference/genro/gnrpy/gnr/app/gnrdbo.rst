==========================================================================================
:mod:`gnr.app.gnrdbo` -- Counters, tables and other services for the hierarchical database
==========================================================================================

* Index of ``gnr.app.gnrdbo`` methods:
	
		* :ref:`gnrapp_gnrdbopkg`
		* :ref:`gnrapp_gnrdbotbl`
		* :ref:`gnrapp_gnrhtbl`
		* :ref:`gnrapp_tblbase`
		* :ref:`gnrapp_tblcounter`
		
* The :ref:`gnrdbo_classes` classes

.. _gnrapp_gnrdbopkg:

:class:`GnrDboPackage`
======================

	.. module:: gnr.app.gnrdbo.GnrDboPackage
	
	========================== ============================
	:meth:`deleteUserObject`   :meth:`loadUserObject`      
	:meth:`getCounter`         :meth:`saveUserObject`      
	:meth:`getLastCounterDate` :meth:`setCounter`          
	:meth:`getPreference`      :meth:`setPreference`       
	:meth:`listUserObject`     :meth:`updateFromExternalDb`
	========================== ============================
	
.. _gnrapp_gnrdbotbl:

:class:`GnrDboTable`
====================

	.. module:: gnr.app.gnrdbo.GnrDboTable
	
	* :meth:`use_dbstores`

.. _gnrapp_gnrhtbl:

:class:`GnrHTable`
==================

	.. module:: gnr.app.gnrdbo.GnrHTable
	
	* :meth:`assignCode`
	* :meth:`htableFields`
	* :meth:`trigger_onInserting`
	* :meth:`trigger_onInserting`
	
.. _gnrapp_tblbase:

:class:`TableBase`
==================

	.. module:: gnr.app.gnrdbo.TableBase
	
	================================== ==================================
	:meth:`hasRecordTags`              :meth:`trigger_setAuditVersionUpd`
	:meth:`setTagColumn`               :meth:`trigger_setRecordMd5`      
	:meth:`sysFields`                  :meth:`trigger_setTSNow`          
	:meth:`trigger_setAuditVersionIns`                                   
	================================== ==================================

.. _gnrapp_tblcounter:

:class:`Table_counter`
======================

	.. module:: gnr.app.gnrdbo.Table_counter
	
	====================== ==========================
	:meth:`config_db`      :meth:`getLastCounterDate`
	:meth:`counterCode`    :meth:`getYmd`            
	:meth:`createCounter`  :meth:`setCounter`        
	:meth:`formatCode`     :meth:`use_dbstores`      
	:meth:`getCounter`                               
	====================== ==========================
	
.. _gnrdbo_classes:

:mod:`gnr.app.gnrdbo`
=====================

.. automodule:: gnr.app.gnrdbo
    :members:
