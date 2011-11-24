.. _macro:

======
macros
======
    
    *Last page update*: |today|
    
    * :ref:`macro_intro`
    * :ref:`fire`
    * :ref:`get`
    * :ref:`publish`
    * :ref:`put`
    * :ref:`set`
    
    * :ref:`macro_examples`:
    
        * :ref:`macro_examples_fire`
        * :ref:`macro_examples_set`
        
.. _macro_intro:
    
introduction
============

    We introduce now the Genro macros:
    
    * They are a shortcut for some javascript functions
    * They can be specified in the javascript events associated with an interface. For example
      you can use them in a :ref:`button` through the :ref:`action_attr` attribute
    * The framework deals gnrjs to the expansion of these macros
    * They can be accessed from their datastore javascript code (i.e. from code written in a .JS
      file and then read without macro-expansion) using simple javascript functions
      
.. _fire:

FIRE
====

    Set a value in the ``datastore``, and then trigger the events associated. After that reset the
    value to zero (without triggering events [#]_). It is used when you need to trigger events through
    a temporary parameter.
    
    For example, ``FIRE goofy='aaa'`` is a shortcut for the following commands::
    
        this.setRelativeData("goofy",aaa)
        this.setRelativeData("goofy",null)
        
    For more information, check the :ref:`macro_examples_fire`
    
.. _get:
    
GET
===

    Read the contents of a value in the :ref:`datastore`
    
    **Example**: ``GET goofy`` is a shortcut for the following command::
    
        this.getRelativeData("goofy");
        
.. _publish:

PUBLISH
=======

    TODO
    
.. _put:

PUT
===
    
    Set a value, but does not trigger the associated events.
    
.. _set:

SET
===

    State a value and triggers any associated events (ie any observers or resolver connected by "^").
    
    For example, ``SET goofy='aaa'`` is a shortcut for the following command::
    
        this.setRelativeData("goofy",aaa);
        
    For more information, check the :ref:`macro_examples_set`
    
.. _macro_examples:

examples
========

.. _macro_examples_fire:

FIRE example
------------

    * `FIRE [example n.1] <http://localhost:8080/macros/1>`_
    * **Description**: an example of the :ref:`fire` :ref:`Genro macro <macro>`
    
      .. note:: example elements' list:
      
                * **classes**: :ref:`gnrcustomwebpage`
                * **components**: :ref:`testhandlerfull`
                * **webpage variables**: :ref:`webpages_py_requires`
                * **widgets**: :ref:`bordercontainer`, :ref:`datacontroller`, :ref:`formbuilder`
                
    * **Code**::
    
        # -*- coding: UTF-8 -*-
        """macros"""

        class GnrCustomWebPage(object):
            py_requires="gnrcomponents/testhandler:TestHandlerFull"
        
            def test_1_fire(self,pane):
                """macro (FIRE)"""
                bc = pane.borderContainer()
                bc.div("""There are three way to use FIRE:""",
                        font_size='.9em',text_align='justify')
                bc.dataController('''alert(msg);''', msg='^.msg')
                fb = bc.formbuilder(cols=2)

                fb.button('Click me!',action="FIRE .msg='Click';")
                fb.div(""" "action="FIRE msg='Click';" [shows an alert message reporting "Click"] """,font_size='.9em')

                fb.button('Click me!',fire_Click = '.msg')
                fb.div(""" "fire_Click = 'msg'" [same result of the previous one]""",font_size='.9em')

                fb.button('Click me!',fire='.msg')
                fb.div(""" "fire='msg'" [shows an alert message reporting "true"] """,font_size='.9em')
                
.. _macro_examples_set:

SET example
------------

    * `SET [example n.1] <http://localhost:8080/macros/2>`_
    * **Description**: an example of the :ref:`fire` :ref:`Genro macro <macro>`
    
      .. note:: example elements' list:
      
                * **classes**: :ref:`gnrcustomwebpage`
                * **components**: :ref:`testhandlerfull`
                * **webpage variables**: :ref:`webpages_py_requires`
                * **widgets**: :ref:`bordercontainer`, :ref:`datacontroller`, :ref:`formbuilder`
                
    * **Code**::
    
        # -*- coding: UTF-8 -*-
        """macros"""

        class GnrCustomWebPage(object):
            py_requires="gnrcomponents/testhandler:TestHandlerFull"
            
            def test_2_set(self,pane):
                """macro (SET)"""
                pane.data('.number', 0)
                pane.dataController("""SET .number=36;""",_fired='^.my_button')
                bc = pane.borderContainer()
                fb = bc.formbuilder(cols=2)
                fb.div("""We gave the value 0 through a data controller. The button
                          contains a trigger for a dataController that has a \"SET\" macro
                          that give \"36\" every time it is clicked""",
                          font_size='.9em', text_align='justify', colspan=2)
                fb.button('36',fire='^.my_button')
                fb.numberSpinner(lbl='number', value='^.number')
            
                fb.div("""This time the button contains directly the \"SET\" macro""",
                          font_size='.9em', text_align='justify', colspan=2)
                fb.button('36', action='SET .number2=36;')
                fb.numberSpinner(lbl='number 2', value='^.number2')
                
**Footnotes:**

.. [#] In this way the trigger can be used more than once time.