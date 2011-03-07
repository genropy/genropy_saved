.. _webpages_webpages:

=======
webpage
=======

    * :ref:`webpages_GnrCustomWebPage`
    * :ref:`webpages_variables`:
    
        * :ref:`webpages_dojo_version`
        * :ref:`webpages_theme`
        * :ref:`webpages_gnrjsversion`
        * :ref:`webpages_maintable`
        * :ref:`webpages_recordlock`
        * :ref:`webpages_user_polling`
        * :ref:`webpages_auto_polling`
        * :ref:`webpages_eagers`
        * :ref:`webpages_py_requires`
        * :ref:`webpages_js_requires`
        * :ref:`webpages_pageOptions`
        * :ref:`webpages_css_requires`
        * :ref:`webpages_auth_tags`
        
.. _webpages_GnrCustomWebPage:

Genro Custom Webpage
====================

    The Genro Custom Webpage is add???(a mixin class?) through which you can build your webpages.
    
    #. A webpage file has to begin with the following declaration line::
    
        class GnrCustomWebPage(object):
        
    #. You may insert some optional :ref:`webpages_variables`. Here we introduce the most commonly used:
    
        * :ref:`webpages_maintable`: allow to create shortcuts for users query
        * :ref:`webpages_py_requires`: allow to include some Genro :ref:`genro_components_index` to your webpage
        * :ref:`webpages_js_requires`: allow to include some javascipt functionality to your webpage
        * :ref:`webpages_css_requires`: allow to include some CSS elements to your webpage
    
    #. You have to define the main method (unless you're using an active component! [#]_)
        
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
                
    In the following sections we describe the :ref:`webpages_variables`.

.. _webpages_variables:

webpages variables
==================

    .. module:: gnr.web.gnrwsgisite_proxy.gnrresourceloader.ResourceLoader
    
    add??? (a short introduction + link to the the :meth:`get_page_class` method)

.. _webpages_dojo_version:

dojo_version
============
    
    * Description: allow to specify the Dojo version of your :ref:`genro_structure_mainproject`. You have to 
      write the version supported without the dot (e.g: write '11' for Dojo '1.1')
    * Default value: the value you specify in the :ref:`siteconfig_dojo` tag of your :ref:`sites_siteconfig` or '11' (i.e: Dojo 1.1)
      if your ``<Dojo>`` tag is ``None``.
      
.. _webpages_theme:

theme
=====

    * Description: allow to change the Dojo page's theme.
    
    .. note:: if you have to configure the Dojo theme for ALL of your webpages, we suggest you to change it into your :ref:`sites_siteconfig` file, changing the :ref:`siteconfig_gui` tag features.
    
    * Default value: the value you specify in the :ref:`siteconfig_gui` tag of your :ref:`sites_siteconfig` or 'tundra' (i.e: Dojo Tundra theme)
    
.. _webpages_gnrjsversion:

gnrjsversion
============

    * Description: Genro Javascript libraries compatible with the relative Dojo version.
    * Default value: the value you specify in the :ref:`siteconfig_jslib` tag of your :ref:`sites_siteconfig` or '11' (i.e: libraries compatible with Dojo 1.1)
    
.. _webpages_maintable:

maintable
=========

    add??? CONTINUE FROM HERE!!
    
    * Description: allow to create shortcuts for users query. add???
    * Default value: ``None``
    
.. _webpages_recordlock:

recordLock
==========

    * Description: add???
    * Default value: ``None``
    
.. _webpages_user_polling:

user_polling
============

    * Description: add???
    * Default value: ``3`` (units: seconds)
    
.. _webpages_auto_polling:

auto_polling
============

    * Description: add???
    * Default value: ``30`` (units: seconds)
    
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

    * Description: a dict with page options. add??? pageOptions = {'enableZoom':False,'openMenu':False}
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

**Footnotes**:

.. [#] For more information on active and passive components, please check the :ref:`components_active_passive` documentation section.