.. _slider:

======
Slider
======
    
    *Last page update*: |today|
    
    .. note:: Slider features:
              
              * **Type**: :ref:`Dojo form widget <dojo_form_widgets>`
              * **Common attributes**: check the :ref:`attributes_index` section
              
    * :ref:`slider_def`
    * :ref:`slider_description`
    * :ref:`slider_attributes`
    * :ref:`slider_examples`: :ref:`slider_examples_simple`

.. _slider_def:

Definition
==========

    .. method:: pane.horizontalSlider([**kwargs])
    
    .. method:: pane.verticalSlider([**kwargs])
    
.. _slider_description:

Description
===========

    Slider is a scale with a handle you can move to select a value.
    You can choose between the horizontalSlider and the verticalSlider.

.. _slider_attributes:

Attributes
==========
    
    **slider attributes**:
    
    * *width*: (horizontalSlider) MANDATORY - define the width of your horizontalSlider
    * *height*: (verticalSlider) MANDATORY - define the height of your verticalSlider
    * *intermediateChanges*: (Boolean) If True, it allows to changes value of slider during slider move
    * *maximum*: Add the maximum value of the slider. Default value is 100
    * *minimum*: Add the minimum value of the slider. Default value is 0
    
.. _slider_examples:

Examples
========

.. _slider_examples_simple:

simple example
--------------

    Let's see a simple example::
    
        class GnrCustomWebPage(object):
            def main(self,root,**kwargs):
                root.horizontalSlider(value='^integer_number',width='200px',
                                      maximum=50, discreteValues=51)
                root.verticalSlider(value='^integer_number', height='100px',minimum=0)