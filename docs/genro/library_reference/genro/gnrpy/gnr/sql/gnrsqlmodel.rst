=================================================
:mod:`gnr.sql.gnrsqlmodel` -- Database Model
=================================================

* Index of ``gnr.sql.gnrsqlmodel`` methods:

    Main classes:
    
    * :ref:`gnrsqlmodel_dbmodel`
    * :ref:`gnrsqlmodel_dbmodelsrc`
    * :ref:`gnrsqlmodel_dbtableobj`
    
    Other classes:
    
    * :ref:`gnrsqlmodel_dbcolumnobj`
    * :ref:`gnrsqlmodel_dbmodelobj`
    * :ref:`gnrsqlmodel_dbpackageobj`
    * :ref:`gnrsqlmodel_modelsrcresolver`
    
* :ref:`gnrsqlmodel_classes`

.. _gnrsqlmodel_dbmodel:

:class:`DbModel`
================

    .. module:: gnr.sql.gnrsqlmodel.DbModel
    
    ========================== =========================
    :meth:`addRelation`        :meth:`load`             
    :meth:`applyModelChanges`  :meth:`package`          
    :meth:`build`              :meth:`packageMixin`     
    :meth:`check`              :meth:`resolveAlias`     
    :meth:`checkRelationIndex` :meth:`save`             
    :meth:`column`             :meth:`table`            
    :meth:`debug`                                       
    ========================== =========================

.. _gnrsqlmodel_dbmodelsrc:

:class:`DbModelSrc`
===================

    .. module:: gnr.sql.gnrsqlmodel.DbModelSrc
    
    ========================== =======================
    :meth:`aliasColumn`        :meth:`package`        
    :meth:`aliasTable`         :meth:`pyColumn`       
    :meth:`column`             :meth:`relation`       
    :meth:`externalPackage`    :meth:`table`          
    :meth:`formulaColumn`      :meth:`table_alias`    
    :meth:`index`              :meth:`virtual_column` 
    ========================== =======================

.. _gnrsqlmodel_dbtableobj:

:class:`DbTableObj`
===================

    .. module:: gnr.sql.gnrsqlmodel.DbTableObj
    
    ============================= ============================ =========================== =======================
    :meth:`afterChildrenCreation` :meth:`getRelationBlock`     :meth:`pkey`                :meth:`rowcaption`     
    :meth:`column`                :meth:`indexes`              :meth:`pkg`                 :meth:`sqlfullname`    
    :meth:`columns`               :meth:`lastTS`               :meth:`queryfields`         :meth:`sqlname`        
    :meth:`doInit`                :meth:`logicalDeletionField` :meth:`relatingColumns`     :meth:`sqlschema`      
    :meth:`fullRelationPath`      :meth:`name_plural`          :meth:`relations_many`      :meth:`table_aliases`  
    :meth:`fullname`              :meth:`newRelationResolver`  :meth:`relations_one`       :meth:`virtual_columns`
    :meth:`getRelation`           :meth:`noChangeMerge`        :meth:`resolveRelationPath`                        
    ============================= ============================ =========================== =======================
    
.. _gnrsqlmodel_dbcolumnobj:

:class:`DbColumnObj`
====================

    .. module:: gnr.sql.gnrsqlmodel.DbColumnObj
    
    * :meth:`doInit`
    * :meth:`relatedColumn`
    * :meth:`relatedColumnJoiner`
    * :meth:`relatedTable`

.. _gnrsqlmodel_dbmodelobj:

:class:`DbModelObj`
===================

    .. module:: gnr.sql.gnrsqlmodel.DbModelObj
    
    * :meth:`getAttr`
    * :meth:`getTag`

.. _gnrsqlmodel_dbpackageobj:

:class:`DbPackageObj`
=====================

    .. module:: gnr.sql.gnrsqlmodel.DbPackageObj
    
    * :meth:`dbtable`
    * :meth:`table`
    * :meth:`tableSqlName`
    * :meth:`tables`

.. _gnrsqlmodel_modelsrcresolver:

:class:`ModelSrcResolver`
=========================

    .. module:: gnr.sql.gnrsqlmodel.ModelSrcResolver
    
    * :meth:`load`
    * :meth:`resolverSerialize`

.. _gnrsqlmodel_classes:

:mod:`gnr.sql.gnrsqlmodel` - The complete reference list
========================================================

.. automodule:: gnr.sql.gnrsqlmodel
    :members:
