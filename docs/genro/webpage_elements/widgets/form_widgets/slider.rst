.. _slider:

======
slider
======
    
    *Last page update*: |today|
    
    .. note:: Slider features:
              
              * **Type**: :ref:`Dojo widget <dojo_widgets>`
              * **Common attributes**: check the :ref:`attributes_index` section
              
    * :ref:`slider_def`
    * :ref:`slider_examples`:
    
        * :ref:`slider_examples_simple`

.. _slider_def:

Definition
==========

    .. method:: pane.horizontalSlider([**kwargs])
    
    .. method:: pane.verticalSlider([**kwargs])
    
                Slider is a scale with a handle you can move to select a value.
                You can choose between the horizontalSlider and the verticalSlider
                
                * **Parameters**:
                
                * **width**: (horizontalSlider) MANDATORY - define the width of your horizontalSlider
                * **height**: (verticalSlider) MANDATORY - define the height of your verticalSlider
                * **intermediateChanges**: (Boolean) If True, it allows to changes value of slider during slider move
                * **minimum**: Add the minimum value of the slider. Default value is 0
                * **maximum**: Add the maximum value of the slider. Default value is 100
                
.. _slider_examples:

Examples
========

.. _slider_examples_simple:

simple example
--------------

    * `horizontal slider [basic] <http://localhost:8080/webpage_elements/widgets/form_widgets/slider/1>`_
    
      .. note:: example elements' list:
      
                * **classes**: :ref:`gnrcustomwebpage`
                * **components**: :ref:`testhandlerfull`
                * **webpage variables**: :ref:`webpages_py_requires`
                * **widgets**: TODO
                
    * **Code**::
    
        TODO