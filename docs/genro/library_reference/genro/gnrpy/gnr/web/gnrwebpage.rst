.. _library_gnrwebpage:

====================================
:mod:`gnr.web.gnrwebpage` - Webpages
====================================
    
    *Last page update*: |today|
    
    **Main class:**
    
    * :ref:`gnrwebpage_gnrwebpage`
    
    **Other classes:**
    
    * :ref:`gnrwebpage_clientdatachange`
    * :ref:`gnrwebpage_clientpagehandler`
    * :ref:`gnrwebpage_gnrgenshipage`
    * :ref:`gnrwebpage_gnrmakopage`
    * :ref:`gnrwebpage_lazybagresolver`
    
    **Complete reference:**
    
    * :ref:`gnrwebpage_classes`

.. _gnrwebpage_gnrwebpage:

:class:`GnrWebPage`
===================

    .. module:: gnr.web.gnrwebpage.GnrWebPage
    
    ================================== =========================== ================================ ================================
    :meth:`addHtmlHeader`              :meth:`getResourceList`     :meth:`newSourceRoot`            :meth:`rpc_getPrinters`         
    :meth:`addToContext`               :meth:`getResourceUri`      :meth:`onBegin`                  :meth:`rpc_getUserPreference`   
    :meth:`app`                        :meth:`getResourceUriList`  :meth:`onDeleted`                :meth:`rpc_main`               
    :meth:`application`                :meth:`getService`          :meth:`onDeleting`               :meth:`rpc_onClosePage`         
    :meth:`btc`                        :meth:`getUserPreference`   :meth:`onEnd`                    :meth:`rpc_ping`                
    :meth:`build_arg_dict`             :meth:`getUuid`             :meth:`onInit`                   :meth:`rpc_relationExplorer`    
    :meth:`call_args`                  :meth:`get_bodyclasses`     :meth:`onIniting`                :meth:`rpc_remoteBuilder`       
    :meth:`callTableMethod`            :meth:`get_call_handler`    :meth:`onMain`                   :meth:`rpc_sendMessageToClient` 
    :meth:`catalog`                    :meth:`get_css_genro`       :meth:`onMainCalls`              :meth:`rpc_setInClientPage`     
    :meth:`checkPermission`            :meth:`get_css_icons`        :meth:`onPreIniting`            :meth:`rpc_setInServer`          
    :meth:`clientPage`                 :meth:`get_css_path`        :meth:`onSaved`                  :meth:`rpc_setStoreSubscription`
    :meth:`collectClientDatachanges`   :meth:`get_css_theme`       :meth:`onSaving`                 :meth:`setInClientData`        
    :meth:`connectionDocument`         :meth:`homeUrl`             :meth:`onServingCss`             :meth:`setJoinCondition`        
    :meth:`connectionDocumentUrl`      :meth:`htmlHeaders`         :meth:`packageUrl`               :meth:`setPreference`           
    :meth:`connectionStore`            :meth:`importResource`      :meth:`pageFolderRemove`         :meth:`setUserPreference`       
    :meth:`connection_id`              :meth:`importTableResource` :meth:`pageStore`                :meth:`subscribeTable`          
    :meth:`externalUrl`                :meth:`instantiateProxies`  :meth:`resolveResourceUri`       :meth:`temporaryDocument`       
    :meth:`externalUrlToken`           :meth:`isDeveloper`         :meth:`rootPage`                 :meth:`temporaryDocumentUrl`    
    :meth:`getAuxInstance`             :meth:`isGuest`             :meth:`rpc_callTableScript`      :meth:`toText`                  
    :meth:`getCallArgs`                :meth:`isLocalizer`         :meth:`rpc_changeLocale`         :meth:`user`                    
    :meth:`getDomainUrl`               :meth:`lazyBag`             :meth:`rpc_doLogin`              :meth:`userDocument`            
    :meth:`getPreference`              :meth:`mainLeftContent`     :meth:`rpc_getAppPreference`     :meth:`userDocumentUrl`         
    :meth:`getPublicMethod`            :meth:`mainLeftTop`         :meth:`rpc_getGridStruct`        :meth:`userStore`               
    :meth:`getResource`                :meth:`mixinComponent`      :meth:`rpc_getPageStoreData`     :meth:`userTags`                
    :meth:`getResourceContent`         :meth:`mtimeurl`            :meth:`rpc_getPrinterAttributes`                                 
    :meth:`getResourceExternalUriList` :meth:`newGridStruct`                                                                        
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
    