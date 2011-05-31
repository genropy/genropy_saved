.. _genro_library_gnrwebpage:

====================================
:mod:`gnr.web.gnrwebpage` - Webpages
====================================

* Index of ``gnr.web.gnrwebpage`` classes:
    
    Main class:
    
    * :ref:`gnrwebpage_gnrwebpage`
    
    Other classes:
    
    * :ref:`gnrwebpage_clientdatachange`
    * :ref:`gnrwebpage_clientpagehandler`
    * :ref:`gnrwebpage_gnrgenshipage`
    * :ref:`gnrwebpage_gnrmakopage`
    * :ref:`gnrwebpage_lazybagresolver`
    
* :ref:`gnrwebpage_classes`

.. _gnrwebpage_gnrwebpage:

:class:`GnrWebPage`
===================

    .. module:: gnr.web.gnrwebpage.GnrWebPage
    
    ================================== =========================== ================================ ================================
    :meth:`addHtmlHeader`              :meth:`getResourceList`     :meth:`newSourceRoot`            :meth:`rpc_getPrinters`         
    :meth:`addToContext`               :meth:`getResourceUri`      :meth:`onBegin`                  :meth:`rpc_onClosePage`         
    :meth:`app`                        :meth:`getResourceUriList`  :meth:`onDeleted`                :meth:`rpc_ping`                
    :meth:`application`                :meth:`getService`          :meth:`onDeleting`               :meth:`rpc_relationExplorer`    
    :meth:`btc`                        :meth:`getUserPreference`   :meth:`onEnd`                    :meth:`rpc_remoteBuilder`       
    :meth:`build_arg_dict`             :meth:`getUuid`             :meth:`onInit`                   :meth:`rpc_sendMessageToClient` 
    :meth:`call_args`                  :meth:`get_bodyclasses`     :meth:`onIniting`                :meth:`rpc_setInClientPage`     
    :meth:`catalog`                    :meth:`get_call_handler`    :meth:`onMain`                   :meth:`rpc_setInServer`         
    :meth:`checkPermission`            :meth:`get_css_genro`       :meth:`onMainCalls`              :meth:`rpc_setStoreSubscription`
    :meth:`clientPage`                 :meth:`get_css_path`        :meth:`onPreIniting`             :meth:`setInClientData`         
    :meth:`collectClientDatachanges`   :meth:`get_css_theme`       :meth:`onSaved`                  :meth:`setJoinCondition`        
    :meth:`connectionDocument`         :meth:`homeUrl`             :meth:`onSaving`                 :meth:`setPreference`           
    :meth:`connectionDocumentUrl`      :meth:`htmlHeaders`         :meth:`onServingCss`             :meth:`setUserPreference`       
    :meth:`connectionStore`            :meth:`importResource`      :meth:`packageUrl`               :meth:`subscribeTable`          
    :meth:`connection_id`              :meth:`importTableResource` :meth:`pageFolderRemove`         :meth:`subscribedTablesDict`    
    :meth:`externalUrl`                :meth:`instantiateProxies`  :meth:`pageStore`                :meth:`temporaryDocument`       
    :meth:`externalUrlToken`           :meth:`isDeveloper`         :meth:`resolveResourceUri`       :meth:`temporaryDocumentUrl`    
    :meth:`getAuxInstance`             :meth:`isGuest`             :meth:`rootPage`                 :meth:`toText`                  
    :meth:`getCallArgs`                :meth:`isLocalizer`         :meth:`rpc_callTableScript`      :meth:`user`                    
    :meth:`getDomainUrl`               :meth:`lazyBag`             :meth:`rpc_changeLocale`         :meth:`userDocument`            
    :meth:`getPreference`              :meth:`mainLeftContent`     :meth:`rpc_doLogin`              :meth:`userDocumentUrl`         
    :meth:`getPublicMethod`            :meth:`mainLeftTop`         :meth:`rpc_getAppPreference`     :meth:`userStore`               
    :meth:`getResource`                :meth:`mixinComponent`      :meth:`rpc_getGridStruct`        :meth:`userTags`                
    :meth:`getResourceContent`         :meth:`mtimeurl`            :meth:`rpc_getPageStoreData`     :meth:`rpc_getUserPreference`   
    :meth:`getResourceExternalUriList` :meth:`newGridStruct`       :meth:`rpc_getPrinterAttributes` :meth:`rpc_main`                
    ================================== =========================== ================================ ================================
    
.. _gnrwebpage_clientdatachange:

:class:`ClientDataChange`
=========================

    .. module:: gnr.web.gnrwebpage.ClientDataChange
    
    * :meth:`update`
    
.. _gnrwebpage_clientpagehandler:

:class:`ClientPageHandler`
==========================

    .. module:: gnr.web.gnrwebpage.ClientPageHandler
    
    * :meth:`copyData`
    * :meth:`jsexec`
    * :meth:`set`
    
.. _gnrwebpage_gnrgenshipage:

:class:`GnrGenshiPage`
======================

    .. module:: gnr.web.gnrwebpage.GnrGenshiPage
    
    * :meth:`genshi_template`
    * :meth:`onPreIniting`
    
.. _gnrwebpage_gnrmakopage:

:class:`GnrMakoPage`
====================

    .. module:: gnr.web.gnrwebpage.GnrMakoPage
    
    * :meth:`mako_template`
    * :meth:`onPreIniting`
    
.. _gnrwebpage_lazybagresolver:

:class:`LazyBagResolver`
========================

    .. module:: gnr.web.gnrwebpage.LazyBagResolver
    
    * :meth:`getSource`
    * :meth:`load`
    
.. _gnrwebpage_classes:

:mod:`gnr.web.gnrwebpage` - The complete reference list
=======================================================

.. automodule:: gnr.web.gnrwebpage
    :members:
    