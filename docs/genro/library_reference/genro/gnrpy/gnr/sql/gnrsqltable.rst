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
    :meth:`attributes`        :meth:`defaultValues`          :meth:`insert`                :meth:`recordCoerceTypes`
    :meth:`baseViewColumns`   :meth:`delete`                 :meth:`insertOrUpdate`        :meth:`relationExplorer`   
    :meth:`batchUpdate`       :meth:`deleteRelated`          :meth:`lastTS`                :meth:`relationName`       
    :meth:`buildrecord`       :meth:`deleteSelection`        :meth:`lock`                  :meth:`relations`          
    :meth:`buildrecord_`      :meth:`empty`                  :meth:`logicalDeletionField`  :meth:`relations_many`     
    :meth:`checkPkey`         :meth:`exception`              :meth:`model`                 :meth:`relations_one`      
    :meth:`check_deletable`   :meth:`existsRecord`           :meth:`newPkeyValue`          :meth:`rowcaption`         
    :meth:`check_updatable`   :meth:`exportToAuxInstance`    :meth:`newrecord`             :meth:`rowcaptionDecode`   
    :meth:`colToAs`           :meth:`frozenSelection`        :meth:`noChangeMerge`         :meth:`sqlWhereFromBag`    
    :meth:`column`            :meth:`fullRelationPath`       :meth:`pkey`                  :meth:`sql_deleteSelection`
    :meth:`columns`           :meth:`getColumnPrintWidth`    :meth:`pkg`                   :meth:`touchRecords`       
    :meth:`columnsFromString` :meth:`getQueryFields`         :meth:`query`                 :meth:`update`             
    :meth:`copyToDb`          :meth:`getResource`            :meth:`readColumns`           :meth:`touchRecords`       
    :meth:`copyToDbstore`     :meth:`importFromAuxInstance`  :meth:`record`                :meth:`writeRecordCluster` 
    :meth:`db`                :meth:`importFromXmlDump`      :meth:`recordAs`              :meth:`xmlDebug`
    :meth:`dbroot`            :meth:`indexes`                :meth:`recordCaption`         :meth:`xmlDump`            
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
    