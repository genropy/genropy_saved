==============================================
:mod:`gnr.app.gnrapp` -- Application Instances
==============================================
    
    *Last page update*: |today|
    
    **Classes**:
    
    * :ref:`gnrapp_gnrapp`
    * :ref:`gnrapp_gnravatar`
    * :ref:`gnrapp_gnrimpexp`
    * :ref:`gnrapp_gnrmixobj`
    * :ref:`gnrapp_gnrmodulefinder`
    * :ref:`gnrapp_gnmoduleloader`
    * :ref:`gnrapp_null_loader`
    * :ref:`gnrapp_gnrpackage`
    * :ref:`gnrapp_gnrpackageplugin`
    * :ref:`gnrapp_gnrsqlappdb`
    * :ref:`gnrapp_reservedtable_error`
    
    **Complete reference**:
    
    * :ref:`gnrapp_classes`
    
.. _gnrapp_gnrapp:

:class:`GnrApp`
===============

    .. module:: gnr.app.gnrapp.GnrApp
    
    ========================== =============================== ============================= ==========================
    :meth:`addDbstore`         :meth:`checkResourcePermission` :meth:`guestLogin`            :meth:`onInited`         
    :meth:`addResourceTags`    :meth:`dropAllDbStores`         :meth:`init`                  :meth:`onIniting`         
    :meth:`authPackage`        :meth:`dropDbstore`             :meth:`instance_name_to_path` :meth:`pkg_name_to_path`      
    :meth:`auth_py`            :meth:`errorAnalyze`            :meth:`loadTestingData`       :meth:`project_path`      
    :meth:`auth_sql`           :meth:`getAuxInstance`          :meth:`load_gnr_config`       :meth:`realPath`          
    :meth:`auth_xml`           :meth:`getAvatar`               :meth:`load_instance_config`  :meth:`sendmail`          
    :meth:`buildLocalization`  :meth:`getPackagePlugins`       :meth:`makeAvatar`            :meth:`set_environment`   
    :meth:`build_package_path` :meth:`getResource`             :meth:`notifyDbEvent`         :meth:`updateLocalization`
    :meth:`changePassword`     :meth:`get_modulefinder`        :meth:`onDbCommitted`         :meth:`validatePassword`  
    ========================== =============================== ============================= ==========================

.. _gnrapp_gnravatar:

:class:`GnrAvatar`
==================

    .. module:: gnr.app.gnrapp.GnrAvatar
    
    * :meth:`addTags`
    * :meth:`as_dict`

.. _gnrapp_gnrimpexp:

:class:`GnrImportException`
===========================

    .. module:: gnr.app.gnrapp.GnrImportException
    
    there is no public method

.. _gnrapp_gnrmixobj:

:class:`GnrMixinObj`
====================

    .. module:: gnr.app.gnrapp.GnrMixinObj
    
    there is no public method
    
.. _gnrapp_gnrmodulefinder:

:class:`GnrModuleFinder`
========================

    .. module:: gnr.app.gnrapp.GnrModuleFinder
    
    * :meth:`find_module`
    
.. _gnrapp_gnmoduleloader:

:class:`GnrModuleLoader`
========================

    .. module:: gnr.app.gnrapp.GnrModuleLoader
    
    * :meth:`load_module`
    
.. _gnrapp_null_loader:

:class:`NullLoader`
===================

    .. module:: gnr.app.gnrapp.NullLoader
    
    * :meth:`load_module`
    
.. _gnrapp_gnrpackage:

:class:`GnrPackage`
===================

    .. module:: gnr.app.gnrapp.GnrPackage
    
    * :meth:`config_attributes`
    * :meth:`configure`
    * :meth:`getPlugins`
    * :meth:`loadPlugins`
    * :meth:`loadTableMixinDict`
    * :meth:`onApplicationInited`
    * :meth:`onAuthentication`
    
.. _gnrapp_gnrpackageplugin:

:class:`GnrPackagePlugin`
=========================

    .. module:: gnr.app.gnrapp.GnrPackagePlugin
    
    there is no public method
    
.. _gnrapp_gnrsqlappdb:

:class:`GnrSqlAppDb`
====================

    .. module:: gnr.app.gnrapp.GnrSqlAppDb
    
    * :meth:`checkTransactionWritable`
    * :meth:`delete`
    * :meth:`getFromStore`
    * :meth:`getResource`
    * :meth:`insert`
    * :meth:`onDbCommitted`
    * :meth:`update`
    
.. _gnrapp_reservedtable_error:

:class:`GnrWriteInReservedTableError`
=====================================

    .. module:: gnr.app.gnrapp.GnrWriteInReservedTableError
    
    there is no public method
    
.. _gnrapp_classes:

:mod:`gnr.app.gnrapp` - The complete reference list
===================================================

.. automodule:: gnr.app.gnrapp
    :members:
    