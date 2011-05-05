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
    
    ================================== ========================== ================================ ================================
    :meth:`addHtmlHeader`              :meth:`getResourceUri`     :meth:`onDeleting`               :meth:`rpc_onClosePage`         
    :meth:`addToContext`               :meth:`getResourceUriList` :meth:`onEnd`                    :meth:`rpc_ping`                
    :meth:`app`                        :meth:`getService`         :meth:`onInit`                   :meth:`rpc_relationExplorer`    
    :meth:`application`                :meth:`getUserPreference`  :meth:`onIniting`                :meth:`rpc_remoteBuilder`       
    :meth:`btc`                        :meth:`getUuid`            :meth:`onMain`                   :meth:`rpc_sendMessageToClient` 
    :meth:`build_arg_dict`             :meth:`get_bodyclasses`    :meth:`onMainCalls`              :meth:`rpc_setInClientPage`     
    :meth:`call_args`                  :meth:`get_call_handler`   :meth:`onPreIniting`             :meth:`rpc_setInServer`         
    :meth:`catalog`                    :meth:`get_css_genro`      :meth:`onSaved`                  :meth:`rpc_setStoreSubscription`
    :meth:`checkPermission`            :meth:`get_css_path`       :meth:`onSaving`                 :meth:`setInClientData`         
    :meth:`clientPage`                 :meth:`get_css_theme`      :meth:`onServingCss`             :meth:`setJoinCondition`        
    :meth:`collectClientDatachanges`   :meth:`homeUrl`            :meth:`packageUrl`               :meth:`setPreference`           
    :meth:`connectionDocument`         :meth:`htmlHeaders`        :meth:`pageFolderRemove`         :meth:`setUserPreference`       
    :meth:`connectionDocumentUrl`      :meth:`instantiateProxies` :meth:`pageStore`                :meth:`subscribeTable`          
    :meth:`connectionStore`            :meth:`isDeveloper`        :meth:`resolveResourceUri`       :meth:`subscribedTablesDict`    
    :meth:`connection_id`              :meth:`isGuest`            :meth:`rootPage`                 :meth:`temporaryDocument`       
    :meth:`externalUrl`                :meth:`isLocalizer`        :meth:`rpc_callTableScript`      :meth:`temporaryDocumentUrl`    
    :meth:`externalUrlToken`           :meth:`lazyBag`            :meth:`rpc_changeLocale`         :meth:`toText`                  
    :meth:`getAuxInstance`             :meth:`mainLeftContent`    :meth:`rpc_doLogin`              :meth:`user`                    
    :meth:`getCallArgs`                :meth:`mainLeftTop`        :meth:`rpc_getAppPreference`     :meth:`userDocument`            
    :meth:`getDomainUrl`               :meth:`mixinComponent`     :meth:`rpc_getGridStruct`        :meth:`userDocumentUrl`         
    :meth:`getPreference`              :meth:`mtimeurl`           :meth:`rpc_getPageStoreData`     :meth:`userStore`               
    :meth:`getPublicMethod`            :meth:`newGridStruct`      :meth:`rpc_getPrinterAttributes` :meth:`userTags`                
    :meth:`getResource`                :meth:`newSourceRoot`      :meth:`rpc_getPrinters`                                          
    :meth:`getResourceExternalUriList` :meth:`onBegin`            :meth:`rpc_getUserPreference`                                    
    :meth:`getResourceList`            :meth:`onDeleted`          :meth:`rpc_main`                                                 
    ================================== ========================== ================================ ================================
    
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
    :noindex: