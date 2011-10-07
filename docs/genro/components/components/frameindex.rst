.. _frameindex:

==========
FrameIndex
==========
    
    *Last page update*: |today|
    
    .. note:: summary of the component requirements:
              
              * It is NOT a :ref:`components_standard`, so you have to import the correct
                package in your :ref:`instances_instanceconfig` file (more information on the
                importation of a package in the :ref:`instanceconfig_packages` section).
                
                For the FrameIndex the package to be imported is the ``adm`` package.
                The syntax is::
                
                    <gnrcore:adm/>
                    
              * It is an :ref:`components_active`. Its :ref:`webpages_py_requires` are::
                
                  py_requires='frameindex'
                  
    * :ref:`fi_intro`
    * :ref:`fi_creation`:
    
        * :ref:`fi_gnrwebpage_init`
        * :ref:`fi_peculiarities`
        
    * :ref:`fi_webpages_variables`
    * :ref:`fi_examples`:
    
        * :ref:`fi_example_index_url`
        
    * :ref:`fi_gui`:
    
        * :ref:`fi_topbar`
        * :ref:`fi_leftbar`: the :ref:`iframemenu_plugin`, the :ref:`batch_monitor`, the :ref:`chat_plugin`
        * :ref:`fi_iframe`
        * :ref:`fi_bottombar`
    
                .. _fi_intro:

introduction
============

    The FrameIndex allow to load the :ref:`webpages <webpage>` in an :ref:`iframe`.
    
    Let's see an image of the FrameIndex GUI:
    
    .. image:: ../../_images/components/frameindex/fi.png
    
    The webpages will take place in the :ref:`fi_iframe`. There are also other three parts (:ref:`fi_topbar`,
    :ref:`fi_leftbar` and :ref:`fi_bottombar`) that allow to interact with the central pane.
    
    So, the FrameIndex GUI can be divided in 4 parts. We remind the description of these parts to
    the :ref:`fi_gui` section. In the next section we start to learn about the creation of a FrameIndex
    page.
    
.. _fi_creation:

creation of a FrameIndex page
=============================

    The FrameIndex component lives in a standard :ref:`webpage`. So, to use the
    FrameIndex you have to create a standard webpage and then you have to personalize it with
    the FrameIndex features. In this section we'll guide you in the creation of a FrameIndex.
    
    If you are creating a :ref:`project`, you have to write the FrameIndex page into your
    index page.
    
    We remember you that in Genro the default name for the index file is (guess what?)
    ``index.py``. However, you can change the default name using the *homepage* attribute of
    the :ref:`siteconfig_wsgi` tag of the :ref:`gnr_siteconfig` file.
    
    To create a FrameIndex page you have to:
    
    * :ref:`fi_gnrwebpage_init`
    * :ref:`add the FrameIndex peculiarities <fi_peculiarities>`
    
.. _fi_gnrwebpage_init:

create a standard GnrCustomWebpage
----------------------------------

    Let's see the code to initiate a GnrCustomWebpage (you can find more information on the
    following two points in the :ref:`gnrcustomwebpage` page):
    
    #. First of all, you have to write some introductory lines::
       
         #!/usr/bin/env python
         # encoding: utf-8
        
    #. Then you have to instantiate a GnrCustomWebPage::
    
        class GnrCustomWebPage(object):
        
.. _fi_peculiarities:

inside the GnrCustomWebPage: the FrameIndex
-------------------------------------------
    
    #. Now you may define inside the GnrCustomWebPage some :ref:`webpage variables
       <fi_webpages_variables>`: they are python variables that allow to customize your
       component. Two of them are mandatory, in particular:
       
       * the :ref:`webpages_py_requires`, that allows to use the FrameIndex component::
       
            py_requires = 'frameindex'
            
       * the ``index_url``, that allows to specify the url of your index page::
       
            index_url = 'a string with the url of the index page'
            
       For an example of the usage of the ``index_url``, check the :ref:`fi_example_index_url`
            
       For the complete list of all the webpage elements, check the :ref:`next <fi_webpages_variables>`
       section.
       
    #. The last thing you must define is a method of the GnrCustomWebPage: the :meth:`pageAuthTags
       <gnr.web._gnrbasewebpage.GnrBaseWebPage.pageAuthTags>` method::
       
           def pageAuthTags(self, method=None, **kwargs):
               return 'user'
               
    #. You can optionally define the :meth:`windowTitle <gnr.web._gnrbasewebpage.GnrBaseWebPage.windowTitle>`
       method::
       
           def windowTitle(self):
               return '!!Title of the window'
               
       If you don't specify the ``windowTitle``, the default is a string with the name of
       the page in which you define the FrameIndex.
       
.. _fi_webpages_variables:

FrameIndex webpage variables
============================

    With the term ``webpages variables`` we mean that there are some defined variables
    that you can use to customize your FrameIndex page. Let's see all of them:
    
    * *plugin_list*: string. Allow to define what frames you want to see in the
      :ref:`fi_leftbar`. You can add:
       
        * the :ref:`iframemenu_plugin` (to add it type "*iframemenu_plugin*")
        * the :ref:`batch_monitor` (to add it type "*batch_monitor*")
        * the :ref:`chat_plugin` (to add it type "*chat_plugin*")
        
        If you don't specify anything, you will find all the three tools.
        
        The syntax is::
        
            plugin_list = 'iframemenu_plugin,batch_monitor,chat_plugin'
            
        To see only the menu plugin, write::
        
            plugin_list = 'iframemenu_plugin'
            
        The buttons that allow to pass from a 
            
    * *custom_plugin_list*: allow to personalize the set of buttons of the :ref:`fi_topbar`
      that manage the :ref:`fi_leftbar`. They are: ``iframemenu_plugin``, ``batch_monitor``,
      ``chat_plugin``, ``menuToggle``, ``refresh``, ``delete``. For a complete description
      of these buttons, check the :ref:`fi_topbar` section
        
        Example:
        
        If you set the custom_plugin_list equal to::
        
            custom_plugin_list = 'refresh,delete'
            
        then the buttons relative to the the :ref:`fi_leftbar` will be the following ones:
        
        .. image:: ../../_images/components/frameindex/custom_plugin.png
        
        where the yellow highlighted buttons are the default buttons of the ``plugin_list``
        webpage variable, while the other two buttons (the ones with the red edge in the
        figure) are the "reload" and the "cancel" buttons (check the :ref:`fi_topbar`
        section for more information)
        
    * *index_url*: string. Allow to specify the url of your index page. For more information
      check the :ref:`fi_example_index_url`
    * *indexTab*: by default it is set to ``False``; you can write a string in place of
      ``False`` to allow to see your index page (defined through the ``index_url`` attribute)
      as a first button of the ``pages buttons`` in the :ref:`fi_topbar` of the FrameIndex page
    * *hideLeftPlugins*: boolean. If ``True``, allow to start a page with the :ref:`fi_leftbar`
      hidden. By default it is ``False``
    * *preferenceTags*: add??? By default it is ``admin``
    
.. _fi_examples:

examples
========

.. _fi_example_index_url:

index_url example
=================

    Let's see this code, that is an example of a complete FrameIndex page::
    
        #!/usr/bin/env python
        # encoding: utf-8
        
        class GnrCustomWebPage(object):
            py_requires = 'frameindex'
            index_url = 'indexcontent.html'
            
            def windowTitle(self):
                return '!!Invoice'
                
            def pageAuthTags(self, method=None, **kwargs):
                return 'user'
                
    In particular, we set::
    
        index_url = 'indexcontent.html'
        
    because we want to use an html page as index page. (you could use a Python page, too)
    
    The ``indexcontent.html`` page must be placed into the resource folder of your package:
    we call this folder ":ref:`public resource <public_resources>`" folder.
    
    The content of the ``indexcontent.html`` could be something like this::
    
        <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
          "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
        <html xmlns="http://www.w3.org/1999/xhtml">
        <head>
            <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
            <title>Invoice</title>
        </head>
        <body>
            <img src='images/money.jpg' alt='Invoice image'/>
        </body>
        </html>
        
.. _fi_gui:

FrameIndex GUI
==============
    
    Let's see an image of the FrameIndex:
    
    .. image:: ../../_images/components/frameindex/fi.png
    
    The FrameIndex GUI is composed by:
    
    * a :ref:`fi_topbar`
    * a :ref:`fi_leftbar`
    * a :ref:`fi_iframe`
    * a :ref:`fi_bottombar`
    
.. _fi_topbar:

top bar
-------

    .. image:: ../../_images/components/frameindex/fi_top.png
    
    The top bar contains (in order from left to right):
    
    * navigation buttons (point 1) - they are (from left to right):
    
        * show/hide button: show/hide the left pane
        * menu button: open the :ref:`iframemenu_plugin`
        * batch button: open the :ref:`batch_monitor`
        * chat button: open the :ref:`chat_plugin`
        
    * pages buttons (point 2): its a series of all the pages opened by the user. The
      current page is highlighted through a different color. In the image there are
      three opened pages (``customers.py``, ``products.py`` and ``invoices.py``) and
      the current opened page is ``products.py``
    * right buttons (point 3):
    
        * reload button: allow to reload the current page
        * close button: allow to close the current page
    
.. _fi_leftbar:

left pane
---------

    The left pane includes an :ref:`iframe` with the following frames:
    
    * the :ref:`iframemenu_plugin`
    * the :ref:`batch_monitor`
    * the :ref:`chat_plugin`
    
.. _iframemenu_plugin:

menu plug-in
------------

    This frame includes the menu of the project. You can customize the menu
    through the :ref:`packages_menu` file of your :ref:`project`.
    
    Let's see an image example:
    
    .. image:: ../../_images/components/frameindex/fi_left_menu.png
    
    The current selected page is highlighted through a different color. Also,
    the menu supports a folder-hierarchy; there will be visualized only the contents
    of a single folder at a time.
    
    In particular, in the image you can see:
    
    * the ``Invoices Tables`` and the ``Utility`` bars are the folders. In particular, the current
      folder selected is the first one
    * ``Customers``, ``Products``, ``Products Type``, ``Invoices``, ``Single Record`` belong to
      the ``Invoices Tables`` folder and ``customers`` is the current opened page
      
.. _batch_monitor:

batch monitor
-------------

    This frame includes the list of all the :ref:`batches <batch>` in execution or executed
    
    .. image:: ../../_images/components/frameindex/fi_left_batch.png
    
.. _chat_plugin:

chat plug-in
------------

    This frame includes the GUI of the :ref:`chat` component
    
    .. image:: ../../_images/components/frameindex/fi_left_chat.png
    
.. _fi_iframe:

central pane
------------
    
    The central pane is used to display the content of your :ref:`webpages <webpage>`
    
.. _fi_bottombar:

bottom bar
----------

    .. image:: ../../_images/components/frameindex/fi_bottom.png
    
    The bottom bar has got:
    
    * (point 1) A link that opens the :ref:`fi_userpreference` dialog; the link is
      represented by the name of the logged people or by the :ref:`package <packages>`
      name (in the image ``invoice`` is the package name)
    * (point 2) A link that allow the user to disconnect himself from the application (in the
      image the open door with the green arrow)
      
.. _fi_userpreference:

user preference
---------------

    .. image:: ../../_images/components/frameindex/userpreference.png
    
    add???
    