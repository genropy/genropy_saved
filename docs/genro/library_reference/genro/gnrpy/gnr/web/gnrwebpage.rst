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
    
    ================================== =============================== ================================ ================================
    :meth:`addHtmlHeader`              :meth:`getResourceUri`          :meth:`newSourceRoot`            :meth:`rpc_getPrinters`
    :meth:`addToContext`               :meth:`getResourceUriList`      :meth:`onBegin`                  :meth:`rpc_getUserPreference`
    :meth:`app`                        :meth:`getService`              :meth:`onClosePage`              :meth:`rpc_main`             
    :meth:`application`                :meth:`getSiteDocument`         :meth:`onDeleted`                :meth:`rpc_onClosePage`      
    :meth:`btc`                        :meth:`getTableResourceContent` :meth:`onDeleting`               :meth:`rpc_ping`             
    :meth:`build_arg_dict`             :meth:`getUserPreference`       :meth:`onEnd`                    :meth:`rpc_remoteBuilder`       
    :meth:`call_args`                  :meth:`getUuid`                 :meth:`onInit`                   :meth:`rpc_sendMessageToClient` 
    :meth:`callTableMethod`            :meth:`get_bodyclasses`         :meth:`onIniting`                :meth:`rpc_setInClientPage`     
    :meth:`catalog`                    :meth:`get_call_handler`        :meth:`onMain`                   :meth:`rpc_setInServer`         
    :meth:`checkPermission`            :meth:`get_css_genro`           :meth:`onMainCalls`              :meth:`rpc_setStoreSubscription`
    :meth:`clientPage`                 :meth:`get_css_icons`           :meth:`onPreIniting`             :meth:`setInClientData`         
    :meth:`collectClientDatachanges`   :meth:`get_css_path`            :meth:`onSaved`                  :meth:`setJoinCondition`        
    :meth:`connectionDocument`         :meth:`get_css_theme`           :meth:`onSaving`                 :meth:`setPreference`           
    :meth:`connectionDocumentUrl`      :meth:`homeUrl`                 :meth:`onServingCss`             :meth:`setTableResourceContent` 
    :meth:`connectionStore`            :meth:`htmlHeaders`             :meth:`packageUrl`               :meth:`setUserPreference`       
    :meth:`connection_id`              :meth:`importResource`          :meth:`pageFolderRemove`         :meth:`setWorkdate`             
    :meth:`externalUrl`                :meth:`importTableResource`     :meth:`pageStore`                :meth:`subscribeTable`      
    :meth:`externalUrlToken`           :meth:`instantiateProxies`      :meth:`resolveResourceUri`       :meth:`tableTemplate`           
    :meth:`getAuxInstance`             :meth:`isDeveloper`             :meth:`relationExplorer`         :meth:`temporaryDocument`       
    :meth:`getCallArgs`                :meth:`isGuest`                 :meth:`rootPage`                 :meth:`temporaryDocumentUrl`    
    :meth:`getDomainUrl`               :meth:`isLocalizer`             :meth:`rpc_callTableScript`      :meth:`toText`                  
    :meth:`getPreference`              :meth:`lazyBag`                 :meth:`rpc_changeLocale`         :meth:`user`                    
    :meth:`getPublicMethod`            :meth:`mainLeftContent`         :meth:`rpc_doLogin`              :meth:`userDocument`            
    :meth:`getResource`                :meth:`mainLeftTop`             :meth:`rpc_getAppPreference`     :meth:`userDocumentUrl`         
    :meth:`getResourceContent`         :meth:`mixinComponent`          :meth:`rpc_getGridStruct`        :meth:`userStore`            
    :meth:`getResourceExternalUriList` :meth:`mtimeurl`                :meth:`rpc_getPageStoreData`     :meth:`userTags`            
    :meth:`getResourceList`            :meth:`newGridStruct`           :meth:`rpc_getPrinterAttributes`                               
    ================================== =============================== ================================ ================================
    
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
    