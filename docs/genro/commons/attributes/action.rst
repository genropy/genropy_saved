.. _action_attr:

======
action
======
    
    *Last page update*: |today|
    
    .. note:: **validity** - the *action* attribute is supported by:
              
              * :ref:`button`
              * :ref:`checkboxcell`
              * :ref:`menu`
              * :ref:`slotbutton`
              
    * :ref:`action_def`
    * :ref:`action_examples`:
    
        * :ref:`action_examples_basic`
        
.. _action_def:

description
===========

    The *action* attribute allows to write javascript code [#]_.
    
    For example, if you use the *action* attribute on a button, the javascript
    code will be executed on button mouse click
    
.. _action_examples:

examples
========

.. _action_examples_basic:

action example
--------------

    * `action [basic] <http://localhost:8080/webpage_elements/widgets/form_widgets/buttons/button/1>`_
    
      .. note:: example elements' list:

                * **classes**: :ref:`gnrcustomwebpage`
                * **components**: :ref:`testhandlerfull`
                * **webpage variables**: :ref:`webpages_py_requires`
                * **widgets**: :ref:`formbuilder`, :ref:`textbox`
                
    * **Code**::
    
        # -*- coding: UTF-8 -*-
        """Buttons"""

        class GnrCustomWebPage(object):
            py_requires="gnrcomponents/testhandler:TestHandlerFull"

            def test_1_action(self,pane):
                """Action attribute"""
                fb = pane.formbuilder(cols=3)
                fb.div('The action attribute allow to write javascript code', colspan=3)
                fb.button('alert', action="alert('Hello!')", tooltip='click me!', colspan=2)
                fb.div('Create an alert message through "action" attribute. There is a tooltip, too',
                        font_size='.9em', text_align='justify')
                fb.button('confirm', action='confirm("Sure?")', colspan=2)
                fb.div('Create a confirm message through \"action\" attribute', font_size='.9em', text_align='justify')
                fb.button('Show screen resolution', showLabel=False,
                           action="SET .res = screen.width+' x '+screen.height;", iconClass='iconbox spanner')
                fb.textbox(value='^.res', width='6em')
                fb.div('Evaluate your screen resolution', font_size='.9em', text_align='justify')
                
**Footnotes**:

.. [#] For more information of the usage of javascript in Genro please check the :ref:`javascript` section.