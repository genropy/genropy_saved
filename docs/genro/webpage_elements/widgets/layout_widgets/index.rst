.. _layout:

==============
layout widgets
==============

    *Last page update*: |today|
    
    * :ref:`layout_intro`
    * :ref:`layout_common_attributes`
    * :ref:`layout_section_index`
    
.. _layout_intro:

introduction
============

    The layout widgets allow to create the webpage's layout. Some of them are inherited from Dojo.
    
    They are:
    
    1. :ref:`Dojo widgets <dojo_widgets>`:
       
    * 1.1 :ref:`accordioncontainer` 
    * 1.2 :ref:`contentpane`
    * 1.3 :ref:`stackcontainer`
    * 1.4 :ref:`tabcontainer`
    
    2. :ref:`Dojo-improved widgets <dojo_improved_widgets>`:
    
    * 2.1 :ref:`bordercontainer`
    
    3. :ref:`Genro widgets <genro_widgets>`:
    
    * 3.1 :ref:`framepane`
    
    .. note:: **Dojo rule**: a :ref:`contentpane` can include a Container (:ref:`bordercontainer`,
              :ref:`tabcontainer`, etc) if and only if the Container will be a UNIQUE child.
              
.. _layout_common_attributes:

common attributes
=================

    There are some commons attributes that you can use with both Dojo and Genro containers:
    you can find the complete list in the :ref:`attributes_index` section.
    
    In particular you can use:
    
    * *datapath*: set the root's path of data. Default value is ``None``. For more details, check
      the :ref:`datapath` page
    * *height*: Set the height of the container. MANDATORY if the container is the father
      container (example: height='100px')
    * *hidden*: if True, allow to hide this widget. Default value is ``False``. For more information,
      check the :ref:`hidden` page
      
    You can add :ref:`css` and :ref:`css3` attributes to your layout widgets
    
.. _layout_section_index:

section index
=============

.. toctree::
    :maxdepth: 1
    :numbered:
    
    accordioncontainer
    contentpane
    stackcontainer
    tabcontainer
    bordercontainer
    framePane