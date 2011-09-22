.. _slider:

======
slider
======
    
    *Last page update*: |today|
    
    **Type**: :ref:`Dojo form widget <dojo_form_widgets>`
    
    .. note:: the Genro sliders has been taken from Dojo without adding any modifies. In this page you will find some interesting features that we want to point up. For more information, check the Dojo's slider documentation.
    
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

    Slider is a scale with a handle you can move to select a value. You can choose between the horizontalSlider and the verticalSlider.

.. _slider_attributes:

Attributes
==========
    
    **slider attributes**:
    
    * *width*: (horizontalSlider) MANDATORY - define the width of your horizontalSlider
    * *height*: (verticalSlider) MANDATORY - define the height of your verticalSlider
    * *intermediateChanges*: (Boolean) If True, it allows to changes value of slider during slider move
    * *maximum*: Add the maximum value of the slider. Default value is 100
    * *minimum*: Add the minimum value of the slider. Default value is 0
    
    **commons attributes**:
    
    * *hidden*: if True, allow to hide this widget. Default value is ``False``. For more information, check the :ref:`hidden` page
    * *label*: You can't use the *label* attribute; if you want to give a label to your widget, check the :ref:`lbl_formbuilder` example
    * *value*: specify the path of the widget's value. For more information, check the :ref:`datapath` page
    * *visible*: if False, hide the widget. For more information, check the :ref:`visible` page

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