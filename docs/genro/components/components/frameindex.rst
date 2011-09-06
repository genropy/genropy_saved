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
    * :ref:`fi_creation`
    * :ref:`fi_gui`:
    
        * :ref:`fi_topbar`
        * :ref:`fi_leftbar`: :ref:`fi_menu_frame`, :ref:`fi_batch_frame`, :ref:`fi_chat_frame`
        * :ref:`fi_iframe`
        * :ref:`fi_bottombar`
    
                .. _fi_intro:

introduction
============

    The FrameIndex allow to load the :ref:`webpages <webpage>` in an :ref:`iframe`.
    
    To use it you have to replace your index file with the syntax that we discuss later
    in the :ref:`fi_creation` section.
    
    Remember also that, by default, the index page is called ``index.py``; however, you
    can change the default name using the *homepage* attribute of the :ref:`siteconfig_wsgi`
    tag of the :ref:`gnr_siteconfig` file
    
.. _fi_creation:

creation of the FrameIndex page
===============================

    a
    
    add??? plugin_list = 'iframemenu_plugin,batch_monitor,chat_plugin'
    
.. _iframemenu_plugin:

menu plug-in
------------

    add???

.. _batch_monitor:

batch monitor
-------------

    add???

.. _chat_plugin:

chat plug-in
------------

    add???
    
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
        
    * pages buttons (point 2) - it includes, from left to right:
    
    *  buttons (point 3) - it includes, from left to right:
    
.. _fi_leftbar:

left pane
---------

    The left pane includes an :ref:`iframe` with the following frames:
    
    * the :ref:`fi_menu_frame`
    * the :ref:`fi_batch_frame`
    * the :ref:`fi_chat_frame`
    
.. _fi_menu_frame:

menu iFrame
^^^^^^^^^^^

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
      
.. _fi_batch_frame:

batch iFrame
^^^^^^^^^^^^

    This frame includes the list of all the executed batch... add???
    
    .. image:: ../../_images/components/frameindex/fi_left_batch.png
    
.. _fi_chat_frame:

chat iFrame
^^^^^^^^^^^

    This frame includes the chat... add???
    
    .. image:: ../../_images/components/frameindex/fi_left_chat.png
    
.. _fi_iframe:

central pane
------------

    .. image:: ../../_images/components/frameindex/fi_iframe.png
    
    The central pane is used to display the content of your :ref:`webpages <webpages_webpages>`.
    
.. _fi_bottombar:

bottom bar
----------

    .. image:: ../../_images/components/frameindex/fi_bottom.png
    
    The bottom bar has got a link that allow the user to disconnect himself from the
    application (point 1). This link is represented by a word with the :ref:`package
    <packages_index>` name (in the image the package name is ``invoice``).
    
    You can customize it by ... add???
    