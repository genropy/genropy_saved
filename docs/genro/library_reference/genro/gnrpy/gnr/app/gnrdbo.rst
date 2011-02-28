==========================================================================================
:mod:`gnr.app.gnrdbo` -- Counters, tables and other services for the hierarchical database
==========================================================================================

* Index of ``gnr.app.gnrdbo`` methods:

    * :ref:`gnrapp_gnrdbopkg`
    * :ref:`gnrapp_gnrdbotbl`
    * :ref:`gnrapp_gnrhtbl`
    * :ref:`gnrapp_tblbase`
    * :ref:`gnrapp_tblcounter`
    * :ref:`gnrapp_tablerecordtag`
    * :ref:`gnrapp_tblrecordtaglink`
    * :ref:`gnrapp_tableuserobject`
    
* :ref:`gnrdbo_classes`

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
    
.. _gnrapp_tablerecordtag:

:class:`Table_recordtag`
========================

    .. module:: gnr.app.gnrdbo.Table_recordtag
    
    * :meth:`config_db`
    * :meth:`setTagChildren`
    * :meth:`trigger_onDeleting`
    * :meth:`trigger_onInserting`
    * :meth:`trigger_onUpdating`
    * :meth:`use_dbstores`
    
.. _gnrapp_tblrecordtaglink:

:class:`Table_recordtag_link`
=============================

    .. module:: gnr.app.gnrdbo.Table_recordtag_link
    
    ======================== ==========================
    :meth:`assignTagLink`    :meth:`getTagLinksBag`
    :meth:`config_db`        :meth:`getTagTable`
    :meth:`getCountLinkDict` :meth:`tagForeignKey`
    :meth:`getTagDict`       :meth:`use_dbstores`
    :meth:`getTagLinks`      
    ======================== ==========================
    
.. _gnrapp_tableuserobject:

:class:`Table_userobject`
=========================

    .. module:: gnr.app.gnrdbo.Table_userobject
    
    * :meth:`config_db`
    * :meth:`deleteUserObject`
    * :meth:`listUserObject`
    * :meth:`loadUserObject`
    * :meth:`saveUserObject`
    * :meth:`use_dbstores`
    
.. _gnrdbo_classes:

:mod:`gnr.app.gnrdbo` - The complete reference list
===================================================

.. automodule:: gnr.app.gnrdbo
    :members:
