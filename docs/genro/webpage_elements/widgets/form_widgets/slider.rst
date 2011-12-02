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
    
        * :ref:`slider_examples_simple_v`
        * :ref:`slider_examples_simple_h`
        * :ref:`slider_examples_attributes`
        
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

.. _slider_examples_simple_v:

simple example [vertical]
-------------------------

    * `vertical slider [basic] <http://localhost:8080/webpage_elements/widgets/form_widgets/slider/1>`_
    
      .. note:: example elements' list:
      
                * **classes**: :ref:`gnrcustomwebpage`
                * **components**: :ref:`testhandlerfull`
                * **webpage variables**: :ref:`webpages_py_requires`
                * **widgets**: :ref:`formbuilder`, :ref:`numbertextbox`
                
    * **Code**::
    
        # -*- coding: UTF-8 -*-
        """Slider"""

        from gnr.core.gnrdecorator import public_method

        class GnrCustomWebPage(object):
            py_requires = "gnrcomponents/testhandler:TestHandlerFull"

            def test_1_simple(self, pane):
                """Simple vertical slider"""
                fb = pane.formbuilder(cols=2)
                fb.div('The slider and the numerical field are linked: change one of them to change them all', colspan=2)
                fb.verticalSlider(value='^.number', height='100px')
                fb.numberTextbox(value='^.number', lbl='height')
        
.. _slider_examples_simple_h:

simple example [horizontal]
---------------------------

    * `horizontal slider [basic] <http://localhost:8080/webpage_elements/widgets/form_widgets/slider/2>`_
    
      .. note:: example elements' list:
      
                * **classes**: :ref:`gnrcustomwebpage`
                * **components**: :ref:`testhandlerfull`
                * **controllers**: :ref:`data`
                * **webpage variables**: :ref:`webpages_py_requires`
                * **widgets**: :ref:`formbuilder`, :ref:`numberspinner`, :ref:`numbertextbox`
                
    * **Code**::
    
        # -*- coding: UTF-8 -*-
        """Slider"""

        from gnr.core.gnrdecorator import public_method

        class GnrCustomWebPage(object):
            py_requires = "gnrcomponents/testhandler:TestHandlerFull"
            
            def test_2_simple(self, pane):
                """Simple horizontal slider"""
                fb = pane.formbuilder(cols=4)
                pane.data('test2.decimals', '2')
                fb.horizontalSlider(value='^.integer_number', width='200px', maximum=50,
                                    discreteValues=51, lbl='!!Integer number')
                fb.numberTextBox(value='^.integer_number', width='11em', colspan=2, readOnly=True)
                fb.div("""With "discreteValues", "minimum" and "maximum" attributes you can allow to
                          write only integer numbers.""")

                fb.horizontalSlider(value='^.float_number', width='200px', minimum=10, lbl='!!Float number')
                fb.numberTextBox(value='^.float_number', width='11em', places='^.decimals', readOnly=True)
                fb.numberSpinner(value='^.decimals', width='4em', min=0, max=15, lbl='decimals')
                fb.div("""Here you can choose the number of decimals.""")
                
.. _slider_examples_attributes:

attributes example
------------------

    * `horizontal slider [attributes] <http://localhost:8080/webpage_elements/widgets/form_widgets/slider/3>`_
    
      .. note:: example elements' list:
      
                * **classes**: :ref:`gnrcustomwebpage`
                * **components**: :ref:`testhandlerfull`
                * **controllers**: :ref:`data`, :ref:`dataformula`
                * **webpage variables**: :ref:`webpages_py_requires`
                * **widgets**: :ref:`button`, :ref:`combobox`, :ref:`filteringselect`,
                  :ref:`formbuilder`, :ref:`numbertextbox`
                
    * **Code**::
    
        # -*- coding: UTF-8 -*-
        """Slider"""

        from gnr.core.gnrdecorator import public_method

        class GnrCustomWebPage(object):
            py_requires = "gnrcomponents/testhandler:TestHandlerFull"
            
            def test_3_hslider(self, pane):
                """widthness"""
                pane = pane.contentPane(height='400px')
                pane.data('.icon', 'icnBaseOk')
                pane.data('.fontfam', 'Courier')
                pane.data('.font', 9)
                pane.dataFormula('.font_size', 'font+umf', font='^.font', umf='^.um_font')

                fb = pane.formbuilder(cols=5, fld_width='6em')
                fb.horizontalslider(value='^.font', minimum=4, maximum=120, width='20em',
                                    discreteValues=117, intermediateChanges=True, lbl='!!Width font')
                fb.numberTextBox(value='^.font', readOnly=True)
                fb.comboBox(value='^.um_font', values='pt,px', default='pt')
                fb.filteringSelect(value='^.fontfam', lbl='Font',
                                   values='Verdana:Verdana,Courier:Courier,mono:Mono,"Comic Sans MS":Comic')
                fb.filteringSelect(value='^.icon', lbl='icon',
                                   values='icnBaseAdd:Add,icnBaseCancel:Cancel,icnBaseDelete:Delete,icnBaseOk:Ok')

                fb = pane.formbuilder()
                fb.button('Save it', action="alert('Saving!')", iconClass='^.icon',
                           font_size='^.font_size', font_family='^.fontfam')
                           