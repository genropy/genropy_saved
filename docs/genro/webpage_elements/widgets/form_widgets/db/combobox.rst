	.. _combobox:

========
ComboBox
========
    
    *Last page update*: |today|
    
    .. note:: ComboBox features:
    
              * **Type**: :ref:`Dojo widget <dojo_widgets>`
              * **Common attributes**: check the :ref:`attributes_index` section
              
    * :ref:`combobox_def`
    * :ref:`combo_examples`:
    
        * :ref:`combo_examples_bag`
        * :ref:`combo_examples_values`
        
.. _combobox_def:

definition
==========

    .. method:: pane.combobox([**kwargs])
    
    Combobox is a graphical user widget that permits the user to select a value from multiple options.
    
    In combobox you have to provide a list of acceptable values: to upload them, you can use a :ref:`bag`
    (:ref:`combo_examples_bag`) or you can use the *values* attribute (:ref:`combo_examples_values`).
    As the user types, partially matched values will be shown in a pop-up menu below the input text box.
    Like an input text field, user can also type values that doesn't belong to the list of accetable ones.
    
    The combobox looks like a :ref:`filteringselect`: the only difference is that it doesn't support keys
    
    * **Parameters**:
    
                      * **default** (or **default_value**): a default value for your combobox
                      * **hasDownArrow**: If True, create the selection arrow. Default value is ``True``
                      * **ignoreCase**: If True, user can write ignoring the case. Default value is ``True``
                      * **values**: Set all the possible values for user choice. Default value is ``None``.
                        For more information, check the :ref:`combo_examples_values` example
                        
.. _combo_examples:

examples
========

.. _combo_examples_values:

"values" example
----------------

    * `comboBox [values] <http://localhost:8080/webpage_elements/widgets/form_widgets/combobox/1>`_
    * **Description**: how to fill a comboBox through "values" attribute
      
      .. note:: 
      
                #. Pay attention not to confuse *value* with *values*: *value* is used to allocate user
                   data in a well determined :ref:`datapath`, while *values* is used to fill the comboBox
                   
                #. Example elements' list:
                
                   * **classes**: :ref:`gnrcustomwebpage`
                   * **components**: :ref:`testhandlerfull`
                   * **webpage variables**: :ref:`webpages_py_requires`
                   
    * **Code**::
    
        # -*- coding: UTF-8 -*-
        """Combobox"""

        from gnr.core.gnrbag import Bag

        class GnrCustomWebPage(object):
            py_requires = "gnrcomponents/testhandler:TestHandlerFull"

            def test_1_values(self, pane):
                """Combobox filled through "values" attribute"""
                pane.combobox(value='^.record.values', values='Football,Golf,Karate',
                              lbl='loaded through values')
                              
.. _combo_examples_bag:

Bag example
-----------

    * `comboBox [Bag] <http://localhost:8080/webpage_elements/widgets/form_widgets/combobox/2>`_
    * **Description**: how to fill a comboBox through a :ref:`bag`
      
      .. note:: 
      
                #. The advantage in using a Bag is that you can add attributes to your records,
                   but you lose the keys (they aren't supported from combobox).
                   Note that the id is set to the :ref:`pkey` attribute, that is the primary key
                   
                #. Example elements' list:
                
                   * **classes**: :ref:`bag`, :ref:`gnrcustomwebpage`
                   * **components**: :ref:`testhandlerfull`
                   * **webpage variables**: :ref:`webpages_py_requires`
                   * **widgets**: :ref:`data`
                   
    * **Code**::
        
        # -*- coding: UTF-8 -*-
        """Combobox"""

        from gnr.core.gnrbag import Bag

        class GnrCustomWebPage(object):
            py_requires = "gnrcomponents/testhandler:TestHandlerFull"
            
            def test_2_bag(self, pane):
                """Combobox filled through a Bag"""
                pane.data('.values.sport', self.sports(), id='.pkey', caption='.Description')
                pane.combobox(value='^.record', storepath='.values.sport')

            def sports(self, **kwargs):
                mytable = Bag()
                mytable['r1.pkey'] = 'SC'
                mytable['r1.Description'] = 'Soccer'
                mytable['r2.pkey'] = 'BK'
                mytable['r2.Description'] = 'Basket'
                mytable['r3.pkey'] = 'TE'
                mytable['r3.Description'] = 'Tennis'
                mytable['r4.pkey'] = 'HK'
                mytable['r4.Description'] = 'Hockey'
                mytable['r5.pkey'] = 'BB'
                mytable['r5.Description'] = 'Baseball'
                mytable['r6.pkey'] = 'SB'
                mytable['r6.Description'] = 'Snowboard'
                return mytable