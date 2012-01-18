.. _textboxes_index:

=========
Textboxes
=========
    
    *Last page update*: |today|
    
    * :ref:`textboxes`
    * :ref:`textboxes_section_index`
    
.. _textboxes:

introduction
============

    The textboxes are form widgets used to insert input data.
    
    There are five different textbox types:
    
    * :ref:`textbox`
    * :ref:`currencytextbox`
    * :ref:`datetextbox`
    * :ref:`numbertextbox`
    * :ref:`timetextbox`
    
    .. note:: The main additional feature to the Dojo textboxes is the compatibility
              with the Genro validations.
              
              For more information, check the :ref:`validations` page
              
.. _textboxes_examples_simple:

simple example
==============

    * `textboxes [basic] <http://localhost:8080/webpage_elements/widgets/form_widgets/textboxes/mixed/1>`_
      
      .. note:: example elements' list:
      
                * **classes**: :ref:`gnrcustomwebpage`
                * **components**: :ref:`testhandlerfull`
                * **webpage variables**: :ref:`webpages_py_requires`
                * **widgets**: :ref:`datetextbox`, :ref:`formbuilder`,
                  :ref:`numbertextbox`, :ref:`textbox`
                  
    * **Code**::
    
        # -*- coding: UTF-8 -*-
        """Mixed"""

        class GnrCustomWebPage(object):
            py_requires = "gnrcomponents/testhandler:TestHandlerFull"

            def test_1_basic(self, pane):
                """Textboxes"""
                fb = pane.formbuilder(fld_width='18em', cols=2)
                fb.textBox(value='^.name', lbl='Name')
                fb.div('textBox')
                fb.textBox(value='^.surname', lbl='Surname')
                fb.div('textBox')
                fb.dateTextbox(value='^.birthday', lbl='Birthday')
                fb.div('dateTextbox')
                fb.dateTextBox(value='^.date', popup=False, lbl='Date (no popup)',
                               tooltip='remember: date format depends on your \"locale\" browser setting')
                fb.div('dateTextbox')
                fb.numberTextBox(value='^.age', lbl='Age')
                fb.div('numberTextbox')
                fb.textBox(value='^.text', lbl='Text')
                fb.div('textbox')
              
.. _textboxes_section_index:

section index
=============

.. toctree::
    :maxdepth: 1
    :numbered:
    
    textbox
    currencytextbox
    datetextbox
    numbertextbox
    timetextbox