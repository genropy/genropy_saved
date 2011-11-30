.. _radiobutton:

===========
RadioButton
===========
    
    *Last page update*: |today|
    
    .. note:: RadioButton
              
              * **Type**: :ref:`Dojo widget <dojo_widgets>`
              * **Common attributes**: check the :ref:`attributes_index` section
              
    * :ref:`rb_def`
    * :ref:`rb_examples`:
    
        * :ref:`rb_examples_basic`
    
.. _rb_def:

definition
==========

    .. automethod:: gnr.web.gnrwebstruct.GnrDomSrc_dojo_11.radiobutton
    
.. _rb_examples:

examples
========

.. _rb_examples_basic:

basic example
-------------

    * `radioButton [basic] <http://localhost:8080/webpage_elements/widgets/form_widgets/radiobutton/1>`_
    
      .. note:: example elements' list:
      
                * **classes**: :ref:`gnrcustomwebpage`
                * **components**: :ref:`testhandlerfull`
                * **webpage variables**: :ref:`webpages_py_requires`
                * **widgets**: :ref:`formbuilder`
                
    * **Code**::
    
        # -*- coding: UTF-8 -*-
        """Radio buttons"""

        class GnrCustomWebPage(object):
            py_requires = "gnrcomponents/testhandler:TestHandlerFull"

            def test_1_basic(self, pane):
                """Simple test"""
                fb = pane.formbuilder(datapath='.radio', cols=1)

                fb.div("""We show you here a simple radio buttons set.
                          The \"group\" attribute allows to create radiobuttons related each others.""")
                fb.div("""You can specify a default selection with \"default_value=True\"""")
                fb.radiobutton(value='^.jazz', group='genre1', label='Jazz')
                fb.radiobutton(value='^.rock', group='genre1', label='Rock')
                fb.radiobutton(value='^.blues', group='genre1', label='Blues', default_value=True)

                pane.div('Here we show you an other radio buttons set.', margin_left='12px')
                fb = pane.formbuilder(datapath='.sex', cols=3, lbl_width='3em', fld_width='4em')
                fb.div('Sex')
                fb.radiobutton(value='^.male', group='genre2', label='M')
                fb.radiobutton(value='^.female', group='genre2', label='F')