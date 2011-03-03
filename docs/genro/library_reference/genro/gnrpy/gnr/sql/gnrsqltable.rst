=============================================
:mod:`gnr.sql.gnrsqltable` -- Database Tables
=============================================

* Index of ``gnr.sql.gnrsqltable`` classes:
    
    Main class:
    
    * :ref:`gnrsqltable_sqltable`
    
    Exceptions classes:
    
    * :ref:`gnrsqltable_gnrsqlsaveexception`
    * :ref:`gnrsqltable_gnrsqldeleteexception`
    * :ref:`gnrsqltable_gnrsqlprotectupdateexception`
    * :ref:`gnrsqltable_gnrsqlprotectdeleteexception`
    * :ref:`gnrsqltable_gnrsqlprotectvalidateexception`
    
* :ref:`gnrsqltable_classes`

.. _genro_sqltable:

:class:`SqlTable`
=================

    .. module:: gnr.sql.gnrsqltable.SqlTable
    
    The Genro :ref:`genro_sqltable` has a consistent number of methods. They are listed here in alphabetical order.
    
    ========================= ============================== ============================= ===========================
    :meth:`attributes`        :meth:`delete`                 :meth:`insertOrUpdate`        :meth:`relationExplorer`   
    :meth:`baseViewColumns`   :meth:`deleteRelated`          :meth:`lastTS`                :meth:`relationName`       
    :meth:`batchUpdate`       :meth:`deleteSelection`        :meth:`lock`                  :meth:`relations`          
    :meth:`buildrecord`       :meth:`empty`                  :meth:`logicalDeletionField`  :meth:`relations_many`     
    :meth:`buildrecord_`      :meth:`exception`              :meth:`model`                 :meth:`relations_one`      
    :meth:`checkPkey`         :meth:`existsRecord`           :meth:`newPkeyValue`          :meth:`rowcaption`         
    :meth:`check_deletable`   :meth:`exportToAuxInstance`    :meth:`newrecord`             :meth:`rowcaptionDecode`   
    :meth:`check_updatable`   :meth:`frozenSelection`        :meth:`noChangeMerge`         :meth:`sqlWhereFromBag`    
    :meth:`colToAs`           :meth:`fullRelationPath`       :meth:`pkey`                  :meth:`sql_deleteSelection`
    :meth:`column`            :meth:`getColumnPrintWidth`    :meth:`pkg`                   :meth:`touchRecords`       
    :meth:`columns`           :meth:`getQueryFields`         :meth:`query`                 :meth:`update`             
    :meth:`columnsFromString` :meth:`getResource`            :meth:`readColumns`           :meth:`touchRecords`       
    :meth:`copyToDb`          :meth:`importFromAuxInstance`  :meth:`record`                :meth:`writeRecordCluster` 
    :meth:`db`                :meth:`importFromXmlDump`      :meth:`recordAs`              :meth:`xmlDebug`           
    :meth:`dbroot`            :meth:`indexes`                :meth:`recordCaption`         :meth:`xmlDump`            
    :meth:`defaultValues`     :meth:`insert`                 :meth:`recordCoerceTypes`                                
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
