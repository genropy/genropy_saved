.. _genro_library_gnrwsgisite:

==========================
:mod:`gnr.web.gnrwsgisite`
==========================

* Index of ``gnr.web.gnrwsgisite`` classes:
    
    Main class:
    
    * :ref:`gnrwsgisite_gnrwsgisite`
    
    Other classes:
    
    * :ref:`gnrwsgisite_sitelock`
    * :ref:`gnrwsgisite_memoize`
    
    Exceptions classes:
    
    * :ref:`gnrwsgisite_gnrsiteexception`
    
* :ref:`gnrwsgisite_classes`

.. _gnrwsgisite_gnrwsgisite:

:class:`GnrWsgiSite`
====================
    
    .. module:: gnr.web.gnrwsgisite.GnrWsgiSite
    
    ============================= ============================= ============================ =============================
    :meth:`adaptStaticArgs`       :meth:`failed_exception`      :meth:`load_gnr_config`      :meth:`pkg_page_url`         
    :meth:`addService`            :meth:`find_gnrjs_and_dojo`   :meth:`load_site_config`     :meth:`resource_name_to_path`
    :meth:`addSiteServices`       :meth:`forbidden_exception`   :meth:`load_webtool`         :meth:`sendMessageToClient`  
    :meth:`addStatic`             :meth:`getPreference`         :meth:`lockRecord`           :meth:`serve_ping`           
    :meth:`build_gnrapp`          :meth:`getService`            :meth:`log_print`            :meth:`serve_tool`           
    :meth:`build_wsgiapp`         :meth:`getStatic`             :meth:`not_found_exception`  :meth:`setPreference`        
    :meth:`callTableScript`       :meth:`getStaticPath`         :meth:`notifyDbEvent`        :meth:`setResultInResponse`  
    :meth:`cleanup`               :meth:`getStaticUrl`          :meth:`onAuthenticated`      :meth:`setUserPreference`    
    :meth:`clearRecordLocks`      :meth:`getUserPreference`     :meth:`onClosePage`          :meth:`set_environment`      
    :meth:`client_exception`      :meth:`get_datachanges`       :meth:`onInited`             :meth:`shared_data`          
    :meth:`connectionLog`         :meth:`get_path_list`         :meth:`onServedPage`         :meth:`siteLock`             
    :meth:`currentPage`           :meth:`guest_counter`         :meth:`onServingPage`        :meth:`site_static_path`     
    :meth:`debugger`              :meth:`handle_clientchanges`  :meth:`on_reloader_restart`  :meth:`site_static_url`      
    :meth:`dispatcher`            :meth:`initializePackages`    :meth:`pageLog`              :meth:`unlockRecord`         
    :meth:`dropConnectionFolder`  :meth:`loadResource`          :meth:`parse_kwargs`         :meth:`webtools_url`         
    :meth:`exception`             :meth:`loadTableScript`       :meth:`parse_request_params` :meth:`zipFiles`             
    ============================= ============================= ============================ =============================
    
.. _gnrwsgisite_sitelock:

:class:`SiteLock`
=================

    .. module:: gnr.web.gnrwsgisite.SiteLock
    
    * :meth:`acquire`
    * :meth:`release`
    
.. _gnrwsgisite_memoize:

:class:`memoize`
================

    .. module:: gnr.web.gnrwsgisite.memoize
    
    * :meth:`cached_call`
    * :meth:`reset`
    
.. _gnrwsgisite_gnrsiteexception:

:class:`GnrSiteException`
=========================

    .. module:: gnr.web.gnrwsgisite.GnrSiteException
    
    there is no public method.

.. _gnrwsgisite_classes:

:mod:`gnr.web.gnrwsgisite` - The complete reference list
========================================================

.. automodule:: gnr.web.gnrwsgisite
    :members:
    