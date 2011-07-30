.. _gnr_siteconfig:

==============
``siteconfig``
==============
    
    *Last page update*: |today|
    
    .. image:: ../../_images/projects/gnr/siteconfig.png
    
    * :ref:`gnr_siteconfig_default`
    * :ref:`sitesconfig_description`
    * :ref:`sitesconfig_auto`
    * :ref:`sitesconfig_tags`:
        
        * :ref:`siteconfig_wsgi`
        * :ref:`siteconfig_jslib`
        * :ref:`siteconfig_gui`
        * :ref:`siteconfig_dojo`
        * :ref:`siteconfig_resources`
      
    The ``siteconfig`` folder includes a single file: ``default.xml``
    
.. _gnr_siteconfig_default:
    
``default.xml``
===============

    .. image:: ../../_images/projects/gnr/site_default.png
    
    The ``default.xml`` of the ``.gnr/siteconfig`` folder set the default values of
    every :ref:`sites_siteconfig` file of all your projects.
    
    You can obviously redefine the values of the ``siteconfig`` file for every project
    you make, setting the features directly in the :ref:`sites_siteconfig` of the
    specific project.
    
.. _sitesconfig_description:

description of the file
=======================

    The ``sitesconfig`` is an XML file that allows to:
    
    * handle the timeout and the refresh of the connection
    * define your project port
    * import dojo and genro engines
    
.. _sitesconfig_auto:
    
autocreation
============
    
    With the :ref:`sites_autofill` the ``siteconfig`` will look like this one::
    
        <?xml version='1.0' encoding='UTF-8'?>
        <GenRoBag>
            <wsgi _T="NN"></wsgi>
            <connection_timeout _T="NN"></connection_timeout>
            <connection_refresh _T="NN"></connection_refresh>
            <dojo _T="NN" version="11"></dojo>
        </GenRoBag>
    
.. _sitesconfig_tags:

Tags
====

    Let's see its content:
    
    * The file begins and ends with a ``<GenRoBag>`` tag: that's because during the
      execution of the project, this file is being converted in a :ref:`bag_intro`.
    * *<connection_timeout>*: handle the connection timeout.
    * *<connection_refresh>*: handle the connection refresh.
    * *<wsgi>*: allow to define some connections properties used by the :ref:`wsgi_intro`.
      For more information, check the :ref:`siteconfig_wsgi` section.
    * *<jslib>*: allow to specify the dojo version used. For more information,
      check the :ref:`siteconfig_jslib` section.
    * *<gui>*: allow to specify the CSS theme. For more information,
      check the :ref:`siteconfig_gui` section.
    * *<dojo*: allow to specify the Dojo version. For more information, check the
      :ref:`siteconfig_dojo` section.
    * *<resources>*: allow to specify the path for common resources. For more
      information, check the :ref:`siteconfig_resources` section.
      
.. _siteconfig_wsgi:

``<wsgi>``
----------

    Allow to define some connections properties used by the :ref:`wsgi_intro`:
    
    * *homepage*: specify the first :ref:`webpages_webpages` opened on your application.
                  **syntax**:
                  
                  ::
                  
                    packageName/pageName
                    
                  Where:
                  
                  * ``packageName`` is the name of the :ref:`package <packages_index>`
                    to which the page belongs to
                  * ``pageName`` is the name of the webpage (without the ``.py`` extension)
                  
                  By default, the ``packageName`` is set to your mainpackage_ and the ``pageName``
                  is set to ``index``
                  
                    **Example**: the following homepage
                    
                    ::
                    
                        <wsgi homepage='invc/my_index'/>
                        
                    allow to start your application with a ``myindex.py`` webpage included
                    into a package called ``invc``.
                    
    * *port*: specify the port number for your applications
    * *reload*: boolean. If ``True``, ... ???
    * *debug*: boolean. If ``True`` and if a programming error is revealed during the execution
               of a :ref:`webpages_webpages`, it allows to send a traceback of the error through
               a WebError Traceback [#]_
               
    This is an example of the ``<wsgi>`` tag::
    
        <wsgi homepage='invc/index' port="8083" reload="true" debug="true"/>
        
    There is also the *mainpackage* property, but we advise you to create it into the local
    :ref:`sites_siteconfig` of your project:
    
    .. _mainpackage:
    
    * *mainpackage*: a string including the name of your main
      :ref:`package <packages_index>`
      
    ::
    
        <wsgi mainpackage="agenda" port="8083" reload="true" debug="false" />
    
.. _siteconfig_jslib:

``<jslib>``
-----------

    Allow to specify the javascript version used:
    
    * *dojo_version*: the Dojo version used. Use the following syntax: '11' for Dojo 1.1,
      '13' for Dojo 1.3, and so on.
    * *gnr_version*: the version of Genro javascript libraries. Use the following syntax:
      '11' for Genro JS 1.1, '13' for Genro JS 1.3, and so on.
      
    This is an example of the ``<jslib>`` tag::
    
        <jslib dojo_version="11" gnr_version='11' />
        
.. _siteconfig_gui:

``<gui>``
---------

    Allow to specify the Genro CSS theme. You can choose between many themes:
    
    * *aqua*
    * *blue*
    * *elephant*
    * *pro*
    
    This is an example of the ``<gui>`` tag::
    
        <gui css_theme='aqua'/>
        
    The Genro CSS themes override the Dojo theme you're using. For more information, check
    the :ref:`css_dojo_themes` and the :ref:`css_themes` sections.
    
.. _siteconfig_dojo:

``<dojo>``
----------

    Allow to specify the Dojo version.
    
    Here we list its attributes:
    
    * *version*: Dojo version. Use the following syntax: '11' for dojo 1.1, '13' for dojo
      1.3, and so on.
    
    This is an example of the ``<dojo>`` tag::
    
        <dojo version="11"></dojo>
        
.. _siteconfig_resources:

``<resources>``
---------------

    Allow to specify the path for common resources.
    
    There are two tags:
    
    * The ``<common/>`` tag: write it to be able to use a lot of Genro tools:
        
        * Genro :ref:`components <component>`
        * Genro :ref:`css_themes`
        
      .. note:: It is strongly recommended to insert this tag.
      
    * The ``<js_libs/>`` tag: write it to be able to use the javascript_resources
      (add??? a link and a relative page!):
      
        * The CKEDITOR add???
      
    If you insert the two tags, your ``<resources>`` tag will be::
        
        <resources >
            <common/>
            <js_libs/>
        </resources>
        
**Footnotes**:

.. [#] The WebError Traceback is a utility of the WebError Python package.
                