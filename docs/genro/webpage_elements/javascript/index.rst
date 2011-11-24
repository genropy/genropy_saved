.. _javascript:

==========
javascript
==========
    
    *Last page update*: |today|
    
    .. warning:: this section is only a sketch
    
.. _js_intro:

introduction
============
    
    TODO
    
    * The javascript arguments function can be shortened in Genro through the ``$`` syntax. Infact,
      the javascript ``arguments[0]`` is equal to ``$1`` (so, pay attention that the index for the
      first arguments in javascript is ``0``, while in Genro syntax the count of the indexes start
      with ``1``)
    * you can use as javascript commands the :ref:`Genro macros <macro>`: TODO ...
    * The string "value" indicates the current value
      
      ::
      
        fb.field('begin_date', validate_onAccept="if (value){SET .end_date=value;}")
        fb.field('end_date')
        
.. _js_section_index:

section index
=============

.. toctree::
    :maxdepth: 1
    :numbered:
    
    macro