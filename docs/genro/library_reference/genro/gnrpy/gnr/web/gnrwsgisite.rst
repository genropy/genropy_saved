.. _library_gnrwsgisite:

==========================
:mod:`gnr.web.gnrwsgisite`
==========================

    *Last page update*: |today|

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
    :meth:`adaptStaticArgs`       :meth:`find_gnrjs_and_dojo`   :meth:`load_webtool`         :meth:`resource_name_to_path`
    :meth:`addService`            :meth:`forbidden_exception`   :meth:`lockRecord`           :meth:`sendMessageToClient`  
    :meth:`addSiteServices`       :meth:`getPreference`         :meth:`log_print`            :meth:`serve_ping`           
    :meth:`addStatic`             :meth:`getService`            :meth:`not_found_exception`  :meth:`serve_tool`           
    :meth:`build_gnrapp`          :meth:`getStatic`             :meth:`notifyDbEvent`        :meth:`setPreference`        
    :meth:`build_wsgiapp`         :meth:`getStaticPath`         :meth:`onAuthenticated`      :meth:`setResultInResponse`  
    :meth:`callTableScript`       :meth:`getStaticUrl`          :meth:`onClosePage`          :meth:`setUserPreference`    
    :meth:`cleanup`               :meth:`getUserPreference`     :meth:`onDbCommitted`        :meth:`set_environment`      
    :meth:`clearRecordLocks`      :meth:`get_datachanges`       :meth:`onInited`             :meth:`shared_data`          
    :meth:`client_exception`      :meth:`get_path_list`         :meth:`onServedPage`         :meth:`siteLock`             
    :meth:`connectionLog`         :meth:`guest_counter`         :meth:`onServingPage`        :meth:`site_static_path`     
    :meth:`currentPage`           :meth:`handle_clientchanges`  :meth:`on_reloader_restart`  :meth:`site_static_url`      
    :meth:`debugger`              :meth:`initializePackages`    :meth:`pageLog`              :meth:`unlockRecord`         
    :meth:`dispatcher`            :meth:`loadResource`          :meth:`parse_kwargs`         :meth:`webtools_url`         
    :meth:`dropConnectionFolder`  :meth:`loadTableScript`       :meth:`parse_request_params` :meth:`zipFiles`   
    :meth:`exception`             :meth:`load_gnr_config`       :meth:`pkg_page_url`         
    :meth:`failed_exception`      :meth:`load_site_config`                                   
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
    