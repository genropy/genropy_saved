==============================================
:mod:`gnr.app.gnrapp` -- Application Instances
==============================================

* Index of ``gnr.app.gnrapp`` methods:
	
	* :ref:`gnrapp_gnrapp`
	* :ref:`gnrapp_gnravatar`
	* :ref:`gnrapp_gnrimpexp`
	* :ref:`gnrapp_gnrmixobj`
	* :ref:`gnrapp_gnrpackage`
	* :ref:`gnrapp_gnrsqlappdb`
	* :ref:`gnrapp_reservedtable_error`
		
* The :ref:`gnrapp_classes` classes

.. _gnrapp_gnrapp:

:class:`GnrApp`
===============

	.. module:: gnr.app.gnrapp.GnrApp
	
	========================== =============================== ============================= ==========================
	:meth:`addDbstore`         :meth:`changePassword`          :meth:`guestLogin`            :meth:`onInited`          
	:meth:`addResourceTags`    :meth:`checkResourcePermission` :meth:`init`                  :meth:`onIniting`         
	:meth:`authPackage`        :meth:`dropAllDbStores`         :meth:`instance_name_to_path` :meth:`pkg_name_to_path`  
	:meth:`auth_py`            :meth:`dropDbstore`             :meth:`loadTestingData`       :meth:`realPath`          
	:meth:`auth_sql`           :meth:`errorAnalyze`            :meth:`load_gnr_config`       :meth:`sendmail`          
	:meth:`auth_xml`           :meth:`getAuxInstance`          :meth:`load_instance_config`  :meth:`set_environment`   
	:meth:`buildLocalization`  :meth:`getAvatar`               :meth:`makeAvatar`            :meth:`updateLocalization`
	:meth:`build_package_path` :meth:`getResource`             :meth:`notifyDbEvent`         :meth:`validatePassword`  
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

	there is no method defined.

.. _gnrapp_gnrmixobj:

:class:`GnrMixinObj`
====================

	.. module:: gnr.app.gnrapp.GnrMixinObj

	there is no method defined.

.. _gnrapp_gnrpackage:

:class:`GnrPackage`
===================

	.. module:: gnr.app.gnrapp.GnrPackage

	* :meth:`config_attributes`
	* :meth:`configure`
	* :meth:`loadTableMixinDict`
	* :meth:`onApplicationInited`
	* :meth:`onAuthentication`

.. _gnrapp_gnrsqlappdb:

:class:`GnrSqlAppDb`
====================

	.. module:: gnr.app.gnrapp.GnrSqlAppDb

	* :meth:`checkTransactionWritable`
	* :meth:`delete`
	* :meth:`getResource`
	* :meth:`insert`
	* :meth:`update`

.. _gnrapp_reservedtable_error:

:class:`GnrWriteInReservedTableError`
=====================================

	.. module:: gnr.app.gnrapp.GnrWriteInReservedTableError

	there is no method defined.

.. _gnrapp_classes:

:mod:`gnr.app.gnrapp`
=====================

.. automodule:: gnr.app.gnrapp
    :members: