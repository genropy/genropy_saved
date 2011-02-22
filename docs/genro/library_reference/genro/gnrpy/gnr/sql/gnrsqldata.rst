===================================================
:mod:`gnr.sql.gnrsqldata` -- Queries and Selections
===================================================

* Index of ``gnr.sql.gnrsql`` methods:

    Main classes:
    
    * :ref:`gnrsqldata_sqlselection`
    * :ref:`gnrsqldata_sqlquery`
    
    Other classes:
    
    * :ref:`gnrsqldata_sqlcompiledquery`
    * :ref:`gnrsqldata_sqldataresolver`
    * :ref:`gnrsqldata_sqlquerycompiler`
    * :ref:`gnrsqldata_sqlrecord`
    * :ref:`gnrsqldata_sqlrecordbag`
    * :ref:`gnrsqldata_sqlrelatedrecordresolver`
    * :ref:`gnrsqldata_sqlrelatedselectionresolver`
    
* :ref:`gnrsqldata_classes`

.. _gnrsqldata_sqlselection:

:class:`SqlSelection`
=====================

    .. module:: gnr.sql.gnrsqldata.SqlSelection
    
    ==================== =========================== ======================== ======================
    :meth:`analyze`      :meth:`iter_dictlist`       :meth:`out_generator`    :meth:`out_xmlgrid`   
    :meth:`apply`        :meth:`iter_pkeylist`       :meth:`out_grid`         :meth:`output`        
    :meth:`buildAsBag`   :meth:`iter_records`        :meth:`out_json`         :meth:`outputTEST`    
    :meth:`buildAsGrid`  :meth:`newRow`              :meth:`out_list`         :meth:`remove`        
    :meth:`colHeaders`   :meth:`out_bag`             :meth:`out_listItems`    :meth:`setKey`        
    :meth:`extend`       :meth:`out_baglist`         :meth:`out_pkeylist`     :meth:`sort`          
    :meth:`filter`       :meth:`out_count`           :meth:`out_recordlist`   :meth:`toTextGen`     
    :meth:`freeze`       :meth:`out_data`            :meth:`out_records`      :meth:`totalize`      
    :meth:`freezeUpdate` :meth:`out_dictlist`        :meth:`out_selection`    :meth:`totalizer`     
    :meth:`getByKey`     :meth:`out_distinct`        :meth:`out_tabtext`      :meth:`totalizerSort` 
    :meth:`insert`       :meth:`out_distinctColumns` :meth:`out_xls`          :meth:`totals`        
    :meth:`iter_data`    :meth:`out_fullgrid`                                                       
    ==================== =========================== ======================== ======================
    
.. _gnrsqldata_sqlquery:

:class:`SqlQuery`
=================

    .. module:: gnr.sql.gnrsqldata.SqlQuery

    ======================== =========================
    :meth:`compileQuery`     :meth:`iterfetch`        
    :meth:`count`            :meth:`selection`        
    :meth:`cursor`           :meth:`servercursor`     
    :meth:`fetch`            :meth:`serverfetch`      
    :meth:`fetchAsBag`       :meth:`setJoinCondition` 
    :meth:`fetchAsDict`      :meth:`test`             
    :meth:`fetchGrouped`                              
    ======================== =========================
.. _gnrsqldata_sqlcompiledquery:

:class:`SqlCompiledQuery`
=========================

    .. module:: gnr.sql.gnrsqldata.SqlCompiledQuery
    
    * :meth:`get_sqltext`

.. _gnrsqldata_sqldataresolver:

:class:`SqlDataResolver`
========================

    .. module:: gnr.sql.gnrsqldata.SqlDataResolver
    
    * :meth:`init`
    * :meth:`onCreate`
    * :meth:`resolverSerialize`

.. _gnrsqldata_sqlquerycompiler:

:class:`SqlQueryCompiler`
=========================

    .. module:: gnr.sql.gnrsqldata.SqlQueryCompiler

    ============================= ========================
    :meth:`compiledQuery`         :meth:`getFieldAlias`   
    :meth:`compiledRecordQuery`   :meth:`getJoinCondition`
    :meth:`expandMultipleColumns` :meth:`init`            
    :meth:`expandPeriod`          :meth:`recordFields`    
    :meth:`getAlias`              :meth:`updateFieldDict` 
    ============================= ========================

.. _gnrsqldata_sqlrecord:

:class:`SqlRecord`
==================

    .. module:: gnr.sql.gnrsqldata.SqlRecord

    ===================== ========================
    :meth:`compileQuery`  :meth:`out_newrecord`   
    :meth:`out_bag`       :meth:`out_record`      
    :meth:`out_dict`      :meth:`output`          
    :meth:`out_json`      :meth:`setJoinCondition`
    ===================== ========================

.. _gnrsqldata_sqlrecordbag:

:class:`SqlRecordBag`
=====================

    .. module:: gnr.sql.gnrsqldata.SqlRecordBag
    
    * :meth:`save`

.. _gnrsqldata_sqlrelatedrecordresolver:

:class:`SqlRelatedRecordResolver`
=================================

    .. module:: gnr.sql.gnrsqldata.SqlRelatedRecordResolver
    
    * :meth:`load`
    * :meth:`resolverSerialize`

.. _gnrsqldata_sqlrelatedselectionresolver:

:class:`SqlRelatedSelectionResolver`
====================================

    .. module:: gnr.sql.gnrsqldata.SqlRelatedSelectionResolver
    
    * :meth:`load`
    * :meth:`resolverSerialize`

.. _gnrsqldata_classes:

:mod:`gnr.sql.gnrsqldata` - The complete reference list
=======================================================

.. automodule:: gnr.sql.gnrsqldata
    :members:
