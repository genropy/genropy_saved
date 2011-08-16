=====================
:mod:`gnr.sql.gnrsql`
=====================
    
    *Last page update*: |today|
    
* Index of ``gnr.sql.gnrsql`` classes:

    Main classes:
    
    * :ref:`gnrsql_gnrsqldb`
    
    Other classes:
    
    * :ref:`gnrsql_dbstoreshandler`
    * :ref:`gnrsql_tempenv`
    
    Exceptions classes:
    
    * :ref:`gnrsql_gnrsqlexception`
    * :ref:`gnrsql_gnrsqlexecexception`
    
* :ref:`gnrsql_classes`

.. _gnrsql_gnrsqldb:

:class:`GnrSqlDb`
=================

    .. module:: gnr.sql.gnrsql.GnrSqlDb
    
    ======================== ========================= ============================== ==============================
    :meth:`analyze`          :meth:`debug`             :meth:`locale`                 :meth:`setConstraintsDeferred`
    :meth:`checkDb`          :meth:`delete`            :meth:`notify`                 :meth:`startup`               
    :meth:`clearCurrentEnv`  :meth:`dropDb`            :meth:`onDbCommitted`          :meth:`table`                 
    :meth:`closeConnection`  :meth:`dropSchema`        :meth:`package`                :meth:`tableMixin`            
    :meth:`colToAs`          :meth:`dump`              :meth:`packageMixin`           :meth:`tableTreeBag`          
    :meth:`commit`           :meth:`execute`           :meth:`packageSrc`             :meth:`tempEnv`               
    :meth:`connection`       :meth:`get_dbname`        :meth:`packages`               :meth:`unfreezeSelection`     
    :meth:`createDb`         :meth:`importModelFromDb` :meth:`query`                  :meth:`update`                
    :meth:`createModel`      :meth:`importXmlData`     :meth:`relationExplorer`       :meth:`updateEnv`             
    :meth:`createSchema`     :meth:`insert`            :meth:`restore`                :meth:`use_store`             
    :meth:`currentEnv`       :meth:`listen`            :meth:`rollback`               :meth:`vacuum`                
    :meth:`dbstores`         :meth:`loadModel`         :meth:`saveModel`              :meth:`workdate`              
    ======================== ========================= ============================== ==============================
    
.. _gnrsql_dbstoreshandler:

:class:`DbStoresHandler`
========================

    .. module:: gnr.sql.gnrsql.DbStoresHandler
    
    * :meth:`add_dbstore_config`
    * :meth:`add_store`
    * :meth:`create_stores`
    * :meth:`dbstore_align`
    * :meth:`dbstore_check`
    * :meth:`drop_dbstore_config`
    * :meth:`load_config`
    * :meth:`save_config`

.. _gnrsql_tempenv:

:class:`TempEnv`
================

    .. module:: gnr.sql.gnrsql.TempEnv

    there is no public method.

.. _gnrsql_gnrsqlexception:

:class:`GnrSqlException`
========================

    .. module:: gnr.sql.gnrsql.GnrSqlException
    
    there is no public method.

.. _gnrsql_gnrsqlexecexception:

:class:`GnrSqlExecException`
============================

    .. module:: gnr.sql.gnrsql.GnrSqlExecException
    
    there is no public method.
    
.. _gnrsql_classes:

:mod:`gnr.sql.gnrsql` - The complete reference list
===================================================

.. automodule:: gnr.sql.gnrsql
    :members:
    