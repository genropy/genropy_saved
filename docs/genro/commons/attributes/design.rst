.. _design:

======
design
======
    
    *Last page update*: |today|
    
    .. note:: **validity** - the *design* attribute is supported by:
              
              * the :ref:`bordercontainer` (a :ref:`Dojo layout element <dojo_layout>`)
              * the :ref:`framepane` (a :ref:`Genro layout element <genro_layout>`)
              
    The *design* attribute is a Dojo attribute.
    
    The borderContainer (or the framePane) operates in a choice of two layout modes:
    the *design* attribute may be set to ``headline`` or ``sidebar``:
    
    * with the ``headline`` layout, the top and bottom sections extend the entire width
      of the box and the remaining regions are placed in the middle:
      
      .. image:: ../../_images/commons/attributes/headline.png
      
    * with the ``sidebar`` layout, the side panels take priority, extending the full height
      of the box:
      
      .. image:: ../../_images/commons/attributes/sidebar.png