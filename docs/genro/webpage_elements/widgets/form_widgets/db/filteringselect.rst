.. _filteringselect:

===============
FilteringSelect
===============
    
    *Last page update*: |today|
    
    .. note:: FilteringSelect features:
              
              * **Type**: :ref:`Dojo widget <dojo_widgets>`
              * **Common attributes**: check the :ref:`attributes_index` section
              
    * :ref:`filteringselect_def`
    * :ref:`filteringselect_examples`:
    
        * :ref:`filteringselect_examples_bag`
        * :ref:`filteringselect_examples_values`
        
.. _filteringselect_def:

definition
==========

    .. method:: pane.filteringSelect([**kwargs])
    
    The filteringSelect is a Dojo widget who suggests to user the possible (and unique!) entries
    of his selection.
    
    FilteringSelect's values are composed by a key and a value (like the Python dictionary's elements):
    user can chooses from values, while in :ref:`datastore` the user's choice is saved through keys.
    User can also freely type text and partially matched values will be shown in a pop-up menu below
    the input text box.
    
    If user types a wrong entry (that is a word that doesn't corresponds to any of the filteringSelect
    values) the key in :ref:`datastore` will be saved as ``undefined``
    
    * **Parameters**:
    
                      * **ignoreCase**: If ``True``, user can write in filteringSelect ignoring the case.
                        Default value is ``True``
    
                      To prepare the filteringSelect key-value pairs, you can use one of these two attributes:
    
                      * **storepath**: specify a path from which the filteringSelect will get values.
                        For more information, check the :ref:`filteringselect_examples_bag`
                      * **values**: Set all the possible values for user choice. For more information,
                        check the :ref:`filteringselect_examples_values`
                        
.. _filteringselect_examples:

examples
========
                
.. _filteringselect_examples_values:

"values" example
----------------

    * `filteringSelect [values] <http://localhost:8080/webpage_elements/widgets/form_widgets/filteringSelect/1>`_
    * **Description**: The "values" attribute allow to define the key/value couples from which user can choose.
    
      The syntax is::
      
        values='key1:value1,key2:value2,...,keyN:valueN'
        
      .. note:: 
      
                #. Pay attention not to confuse *value* with *values*: *value* is used to locate
                   user data in a well determined :ref:`datapath`, while *values* is used to fill
                   the filteringSelect
                   
                #. Unlike Dojo, actually filteringSelect doesn't warn user for its wrong insertion.
                   You can add a warning for the user through a *validate* attribute (see :ref:`validations`)
                   
                #. Example elements' list:
                   
                    * **classes**: :ref:`gnrcustomwebpage`
                    * **components**: :ref:`testhandlerfull`
                    * **webpage variables**: :ref:`webpages_py_requires`
                    * **widgets**: :ref:`formbuilder`
                    
    * **Code**::
    
        # -*- coding: UTF-8 -*-
        """filteringSelect"""

        from gnr.core.gnrbag import Bag

        class GnrCustomWebPage(object):
            py_requires = "gnrcomponents/testhandler:TestHandlerFull"

            def test_1_values(self, pane):
                """values example"""
                fb = pane.formbuilder(cols=2)
                fb.filteringSelect(value='^.sport',
                                   values="""SC:Soccer,BK:Basket,HK:Hockey,
                                             TE:Tennis,BB:Baseball,SB:Snowboard'""")
                fb.div('Values loaded through \"values\" attribute')
                
.. _filteringselect_examples_bag:
	
Bag example
-----------

    * `filteringSelect [Bag] <http://localhost:8080/webpage_elements/widgets/form_widgets/filteringSelect/2>`_
    * **Description**: how to fill a filteringSelect through a :ref:`bag`.
      
      :ref:`data` is a :ref:`controller <controllers>` that calls the sports() method. This method
      creates and fills a :ref:`bag` with some keys and values. These values are stored in the same
      path of the filteringSelect's *storepath* (in this case, the relative path "bag").
      Lastly, user choice will be save at the path: "value_bag" through the key value
      
      .. note:: example elements' list:
      
                * **classes**: :ref:`bag`, :ref:`gnrcustomwebpage`
                * **components**: :ref:`testhandlerfull`
                * **webpage variables**: :ref:`webpages_py_requires`
                * **widgets**: :ref:`data`, :ref:`formbuilder`
                
    * **Code**::
    
        # -*- coding: UTF-8 -*-
        """filteringSelect"""

        from gnr.core.gnrbag import Bag

        class GnrCustomWebPage(object):
            py_requires = "gnrcomponents/testhandler:TestHandlerFull"
            
            def test_2_bag(self, pane):
                """Bag example"""
                fb = pane.formbuilder(cols=2)
                pane.data('.bag', self.sports(), id='.pkey', caption='.Description')
                fb.filteringSelect(value='^.value_bag', storepath='.bag')
                fb.div('Values loaded through a Bag')

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