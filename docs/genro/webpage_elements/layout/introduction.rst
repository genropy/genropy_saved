.. _layout_introduction:

============
Introduction
============
    
    *Last page update*: |today|
    
    Genro inherits some of its forms (containers and panes) directly from Dojo: the :ref:`dojo_layout`
    There are also some layout elements built directly through GenroPy: the :ref:`genro_layout`
    
    .. warning:: (Dojo rule): a :ref:`contentpane` can include a Container (:ref:`bordercontainer`,
                 :ref:`tabcontainer`, etc) if and only if the Container will be a UNIQUE child.
                 
.. _dojo_layout:

Dojo layout elements
====================
    
    The Dojo layout elements are:
    
    * the :ref:`accordioncontainer`
    * the :ref:`bordercontainer`
    * the :ref:`contentpane`
    * the :ref:`splitcontainer`
    * the :ref:`stackcontainer`
    * the :ref:`tabcontainer`
    
.. _genro_layout:

Genro layout elements
=====================
    
    The Genro layout elements are:
    
    * the :ref:`framepane`
    
.. _layout_common_attributes:

common attributes
=================

    There are some commons attributes that you can use with both Dojo and Genro containers:
    
    * *datapath*: set the root's path of data. Default value is ``None``. For more details, check
      the :ref:`datapath` page
    * *height*: Set the height of the container. MANDATORY if the container is the father container (example: height='100px')
    * *hidden*: if True, allow to hide this widget. Default value is ``False``. For more information,
      check the :ref:`hidden` page
    * *visible*: if False, hide the widget. For more information, check the :ref:`visible` page
    
    You can obviously add :ref:`css` to your containers.
