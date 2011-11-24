.. _library_gnrsqltable:

=============================================
:mod:`gnr.sql.gnrsqltable` -- Database Tables
=============================================
    
    *Last page update*: |today|
    
    **Main class:**
    
    * :ref:`gnrsqltable_sqltable`
    
    **Exceptions classes:**
    
    * :ref:`gnrsqltable_gnrsqlsaveexception`
    * :ref:`gnrsqltable_gnrsqldeleteexception`
    * :ref:`gnrsqltable_gnrsqlprotectupdateexception`
    * :ref:`gnrsqltable_gnrsqlprotectdeleteexception`
    * :ref:`gnrsqltable_gnrsqlprotectvalidateexception`
    
    **Complete reference**:
    
    * :ref:`gnrsqltable_classes`
    
.. _gnrsqltable_sqltable:

:class:`SqlTable`
=================

    .. module:: gnr.sql.gnrsqltable.SqlTable
    
    This class has a consistent number of methods. They are listed here in alphabetical order.
    
    ========================= ============================== ============================= ===========================
    :meth:`attributes`        :meth:`deleteSelection`        :meth:`model`                 :meth:`relations_many`      
    :meth:`baseViewColumns`   :meth:`diagnostic_errors`      :meth:`newPkeyValue`          :meth:`relations_one`      
    :meth:`batchUpdate`       :meth:`diagnostic_warnings`    :meth:`newrecord`             :meth:`rowcaption`         
    :meth:`buildrecord`       :meth:`empty`                  :meth:`noChangeMerge`         :meth:`rowcaptionDecode`   
    :meth:`buildrecord_`      :meth:`exception`              :meth:`onInited`              :meth:`sqlWhereFromBag`    
    :meth:`checkPkey`         :meth:`existsRecord`           :meth:`onIniting`             :meth:`sql_deleteSelection`
    :meth:`check_deletable`   :meth:`exportToAuxInstance`    :meth:`pkey`                  :meth:`touchRecords`              
    :meth:`check_updatable`   :meth:`frozenSelection`        :meth:`pkg`                   :meth:`trigger_onDeleted`    
    :meth:`checkDuplicate`    :meth:`fullRelationPath`       :meth:`protect_delete`        :meth:`trigger_onDeleting`    
    :meth:`colToAs`           :meth:`getColumnPrintWidth`    :meth:`protect_update`        :meth:`trigger_onInserted` 
    :meth:`column`            :meth:`getQueryFields`         :meth:`protect_validate`      :meth:`trigger_onInserting`     
    :meth:`columns`           :meth:`getResource`            :meth:`query`                 :meth:`trigger_onUpdated`              
    :meth:`columnsFromString` :meth:`importFromAuxInstance`  :meth:`readColumns`           :meth:`trigger_onUpdating` 
    :meth:`copyToDb`          :meth:`importFromXmlDump`      :meth:`record`                :meth:`touchRecords`       
    :meth:`copyToDbstore`     :meth:`indexes`                :meth:`recordAs`              :meth:`update`             
    :meth:`db`                :meth:`insert`                 :meth:`recordCaption`         :meth:`touchRecords`       
    :meth:`dbroot`            :meth:`insertOrUpdate`         :meth:`recordCoerceTypes`     :meth:`writeRecordCluster` 
    :meth:`defaultValues`     :meth:`lastTS`                 :meth:`relationExplorer`      :meth:`xmlDebug`
    :meth:`delete`            :meth:`lock`                   :meth:`relationName`          :meth:`xmlDump`            
    :meth:`deleteRelated`     :meth:`logicalDeletionField`   :meth:`relations`             
    ========================= ============================== ============================= ===========================
    
.. _gnrsqltable_gnrsqlsaveexception:

:class:`GnrSqlSaveException`
============================

    .. module:: gnr.sql.gnrsqltable.GnrSqlSaveException
    
    there is no public method.

.. _gnrsqltable_gnrsqldeleteexception:

:class:`GnrSqlDeleteException`
==============================

    .. module:: gnr.sql.gnrsqltable.GnrSqlDeleteException
    
    there is no public method.

.. _gnrsqltable_gnrsqlprotectupdateexception:

:class:`GnrSqlProtectUpdateException`
=====================================

    .. module:: gnr.sql.gnrsqltable.GnrSqlProtectUpdateException
    
    there is no public method.

.. _gnrsqltable_gnrsqlprotectdeleteexception:

:class:`GnrSqlProtectDeleteException`
=====================================

    .. module:: gnr.sql.gnrsqltable.GnrSqlProtectDeleteException
    
    there is no public method.

.. _gnrsqltable_gnrsqlprotectvalidateexception:

:class:`GnrSqlProtectValidateException`
=======================================

    .. module:: gnr.sql.gnrsqltable.GnrSqlProtectValidateException
    
    there is no public method.
    
.. _gnrsqltable_classes:

:mod:`gnr.sql.gnrsqltable` - The complete reference list
========================================================

.. automodule:: gnr.sql.gnrsqltable
    :members:
    