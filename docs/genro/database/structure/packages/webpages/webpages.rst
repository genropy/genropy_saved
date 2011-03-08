.. _webpages_webpages:

================
GnrCustomWebPage
================

    * :ref:`webpages_introduction`
    * :ref:`webpages_GnrCustomWebPage`
    * :ref:`webpages_variables`:
    
        * Components variables: :ref:`webpages_py_requires`
        * CSS variables: :ref:`webpages_css_requires`, :ref:`webpages_theme`
        * Dojo variables: :ref:`webpages_dojo_source`, :ref:`webpages_dojo_theme`, :ref:`webpages_dojo_version`
        * Javascript variables: :ref:`webpages_js_requires`
        * Page options: :ref:`webpages_pageOptions`
        * Polling variables: :ref:`webpages_auto_polling`, :ref:`webpages_user_polling`
        * Other variables: :ref:`webpages_auth_tags`, :ref:`webpages_eagers`, :ref:`webpages_gnrjsversion`,
          :ref:`webpages_maintable`, :ref:`webpages_recordlock`
        
.. _webpages_introduction:

Introduction on a GnrCustomWebPage
==================================

    Genro provides the application GUI using webpages. GnrCustomWebPage. The standard usage of Genro GnrCustomWebPages is to use them in a combo with some :ref:`model_table`\s to create a DBMS :ref:`genro_structure_mainproject`.
    
    You can act on a Genro webpage through:
    
    * **Widgets elements** - Used to create the webpage's layout and to introduce the input elements (button, checkbox, etc).
    
        * Check the :ref:`genro_widgets_introduction`;
        * description and list of all the :ref:`genro_widgets_index`.
    
    * **HTML elements**:
    
        * Check the :ref:`genro_html_introduction`.
    
    * **CSS elements**:
    
        * Check the :ref:`genro_css`.
    
    * **data elements** - Used to define variables from server to client.
    
        * Check the :ref:`genro_data` page.
        
    * **dataRemote elements** - Synchronous rpc.
        
        * Check the :ref:`genro_dataremote` page.
    
    * **controller elements** - They receive input and initiate a response by making calls on model objects.
        
        * Check the :ref:`genro_controllers_intro`;
        * list of :ref:`genro_datacontroller_index`.
    
    Please check every relative section (clicking on their name) to master the language that Genro uses to handle these different tools.
    
    We are going now to introduce the :ref:`webpages_GnrCustomWebPage`, the standard class used to build the webpages.

.. _webpages_GnrCustomWebPage:

GnrCustomWebPage
================

    The GnrCustomWebPage (Genro Custom Webpage) is add???(a mixin class?) through which you can build your webpages.
    
    #. A webpage file has to begin with a line code that specify the location to the python executable in your machine::
    
        #!/usr/bin/env python
        
    #. Then you have to (optionally) specify the encoding you are using::
        
        # encoding: utf-8
    
    #. Then you have to introduce the GnrCustomWebPage class with the following declaration line::
    
        class GnrCustomWebPage(object):
        
    #. You may insert some optional :ref:`webpages_variables`. Here we introduce the most commonly used:
    
        * :ref:`webpages_maintable`: allow to create shortcuts for users query
        * :ref:`webpages_py_requires`: allow to include some Genro :ref:`genro_components_index` to your webpage
        * :ref:`webpages_js_requires`: allow to include some javascipt functionality to your webpage
        * :ref:`webpages_css_requires`: allow to include some :ref:`genro_css` to your webpage
    
    #. You have to define the main method (unless you're using an active component [#]_)
        
    Let's see now an example of a complete heading of a webpage::
    
        #!/usr/bin/env python
        # encoding: utf-8
        # Created by me on 2011-01-25.
        # Copyright (c) 2011 Softwell. All rights reserved.
        
        class GnrCustomWebPage(object):
            maintable = 'agenda.contact'
            py_requires = 'public:Public,standard_tables:TableHandler,public:IncludedView'
            css_requires = 'public'
            
            def main(self,root,**kwargs):
                bc = root.borderContainer()
                bc.div('Hello!')
                # Here goes the rest of your code...
                
    In the following section we describe the :ref:`webpages_variables`.

.. _webpages_variables:

webpages variables
==================

    .. module:: gnr.web.gnrwsgisite_proxy.gnrresourceloader.ResourceLoader
    
    With the term ``webpages variables`` we mean that Genro provides some defined variables that you can use to customize your webpages.
    
    (You can check the method that handle the webpages variables: the :meth:`get_page_class` method)
    
.. _webpages_dojo_theme:

dojo_theme
==========

    * Description: allow to change the Dojo theme of your webpage
    * Default value: *tundra*
    * Compatible themes:
    
        * Dojo 1.1: *nihilo*, *soria*, *tundra*
        * Dojo 1.5: *claro*, *nihilo*, *soria*, *tundra*
        
    * Example::
        
        dojo_theme = 'nihilo'
    
.. _webpages_dojo_version:

dojo_version
============
    
    * Description: allow to specify the Dojo version of your :ref:`genro_structure_mainproject`. You have to
      write the version supported without the dot (e.g: write '11' for Dojo '1.1')
    * Default value: the value you specify in the :ref:`siteconfig_dojo` tag of your :ref:`sites_siteconfig` or '11' (i.e: Dojo 1.1)
      if your ``<Dojo>`` tag is ``None``.
    * Example::
    
        dojo_version = '11'
    
.. _webpages_theme:

theme
=====

    * Description: allow to change the Genro's page theme. A Genro theme add some features to the Dojo theme you choose for your project.
    
    .. note:: to change the Dojo theme, you have to change it into your :ref:`sites_siteconfig` file, changing the features of the :ref:`siteconfig_gui` tag.
    
    * Default value: the value you specify in the :ref:`siteconfig_gui` tag of your :ref:`sites_siteconfig`
      or 'tundra' (i.e: Dojo Tundra theme)
    * Example::
    
        theme = 'aqua' add???
    
.. _webpages_gnrjsversion:

gnrjsversion
============

    * Description: Genro Javascript libraries compatible with the relative Dojo version.
    * Default value: the value you specify in the :ref:`siteconfig_jslib` tag of your :ref:`sites_siteconfig` or '11' (i.e: libraries compatible with Dojo 1.1)
    * Example::
    
        gnrjsversion = '11'
    
    .. _webpages_maintable:

maintable
=========
    
    * Description: allow to create shortcuts for users query through the :ref:`genro_field` attribute.
    * Default value: ``None``
    * Example: add???
    
.. _webpages_recordlock:

recordLock
==========

    * Description: add???
    * Default value: add???
    * Example: add???
    
.. _webpages_user_polling:

user_polling
============

    * Description: add???
    * Default value: ``3`` (units: seconds)
    * Example::
    
        user_polling = 1
        
    .. _webpages_auto_polling:

auto_polling
============

    * Description: add???
    * Default value: ``30`` (units: seconds)
    * Example::
    
        auto_polling = 5
    
    .. _webpages_eagers:

eagers
======

    * Description: add???
    * Default value: ``add???``
    
.. _webpages_py_requires:

py_requires
===========

    * Description: add???
    * Default value: ``add???``
    
.. _webpages_js_requires:

js_requires
===========

    * Description: add???
    * Default value: ``add???``
    
.. _webpages_pageOptions:

pageOptions
===========

    * Description: a dict with page options. add??? --> pageOptions = {'enableZoom':False,'openMenu':False}
    * Default value: ``add???``
    
.. _webpages_css_requires:

css_requires
============

    * Description: add??? With the *css_requires* you can specify the path of your CSS files ...
    * Default value: ``add???``

.. _webpages_auth_tags:

auth_tags
=========

    * Description: add???
    * Default value: ``add???``

.. _webpages_dojo_source:

dojo_source
===========

    add???
    
    * Description: add???
    * Default value: boolean. Default value is add???(``True``?)
    **Examples**:

**Footnotes**:

.. [#] For more information on active and passive components, please check the :ref:`components_active_passive` documentation section.