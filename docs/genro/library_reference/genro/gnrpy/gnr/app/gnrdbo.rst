==========================================================================================
:mod:`gnr.app.gnrdbo` -- Counters, tables and other services for the hierarchical database
==========================================================================================

	* Indexes:
	
		* :ref:`gnrapp_gnrdbopkg`
		* :ref:`gnrapp_gnrdbotbl`
		* :ref:`gnrapp_gnrhtbl`
		* :ref:`gnrapp_tblbase`
		* :ref:`gnrapp_tblcounter`
		
	* :ref:`gnrdbo_classes`

.. _gnrapp_gnrdbopkg:

the :class:`GnrDboPackage` class methods
========================================

	.. module:: gnr.app.gnrdbo.GnrDboPackage
	
	========================== ============================
	:meth:`deleteUserObject`   :meth:`loadUserObject`      
	:meth:`getCounter`         :meth:`saveUserObject`      
	:meth:`getLastCounterDate` :meth:`setCounter`          
	:meth:`getPreference`      :meth:`setPreference`       
	:meth:`listUserObject`     :meth:`updateFromExternalDb`
	========================== ============================
	
.. _gnrapp_gnrdbotbl:

the :class:`GnrDboTable` class methods
========================================

	.. module:: gnr.app.gnrdbo.GnrDboTable
	
	* :meth:`use_dbstores`

.. _gnrapp_gnrhtbl:

the :class:`GnrHTable` class methods
========================================

	.. module:: gnr.app.gnrdbo.GnrHTable
	
	* :meth:`assignCode`
	* :meth:`htableFields`
	* :meth:`trigger_onInserting`
	* :meth:`trigger_onInserting`
	
.. _gnrapp_tblbase:

the :class:`TableBase` class methods
====================================

	.. module:: gnr.app.gnrdbo.TableBase
	
	================================== ==================================
	:meth:`hasRecordTags`              :meth:`trigger_setAuditVersionUpd`
	:meth:`setTagColumn`               :meth:`trigger_setRecordMd5`      
	:meth:`sysFields`                  :meth:`trigger_setTSNow`          
	:meth:`trigger_setAuditVersionIns`                                   
	================================== ==================================

.. _gnrapp_tblcounter:

the :class:`Table_counter` class methods
========================================

	.. module:: gnr.app.gnrdbo.Table_counter
	
	====================== ==========================
	:meth:`config_db`      :meth:`getLastCounterDate`
	:meth:`counterCode`    :meth:`getYmd`            
	:meth:`createCounter`  :meth:`setCounter`        
	:meth:`formatCode`     :meth:`use_dbstores`      
	:meth:`getCounter`                               
	====================== ==========================
	
.. _gnrdbo_classes:

the :mod:`gnr.app.gnrdbo` classes
=================================

.. automodule:: gnr.app.gnrdbo
    :members:
