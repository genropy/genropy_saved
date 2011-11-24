.. _tabcontainer:

============
TabContainer
============
    
    *Last page update*: |today|
    
    .. note:: TabContainer features:
              
              * **Type**: :ref:`Dojo widget <dojo_widgets>`
              * **Common attributes**: check the :ref:`attributes_index` section
              
    * :ref:`tab_definition`
    * :ref:`tab_attributes`
    * :ref:`tab_examples`:
    
        * :ref:`tab_examples_simple`
        * :ref:`tab_tabposition`
        * :ref:`tab_remote`
        
.. _tab_definition:

Definition
==========

    .. method:: pane.tabContainer([**kwargs])

    A TabContainer is a container that has multiple panes, but shows only one pane at a time.
    There are a set of tabs corresponding to each pane, where each tab has the title of the pane.

.. _tab_attributes:

Attributes
==========

    **tabContainer's attributes**:
    
    * *tabPosition*: define the place of the paneContainer's labels. Default value is ``top-h``.
      For all supported possibilities, check the :ref:`tab_tabposition`

    * *selected*: Allow to specify the pane to visualize. You will find in the :ref:`datastore`
                  the current selected tab as a type-number into a specific folder. If you don't
                  specify it, then the first pane will be visualized (but in this case you have
                  to pass it as a ``**kwargs``)
                  
    **attributes of the tabContainer's children (paneContainers)**:
    
    * *title*: the pane title shown on the relative pane tab
    
.. _tab_examples:

Examples
========

.. _tab_examples_simple:

simple example
--------------

    * `tabContainer [basic] <http://localhost:8080/webpage_elements/widgets/layout/tabcontainer/1>`_
      
      .. note:: example elements' list:
                
                * **classes**: :ref:`gnrcustomwebpage`
                * **components**: :ref:`testhandlerfull`
                * **webpage variables**: :ref:`webpages_py_requires`
                * **widgets**: :ref:`contentpane`
                  
    * **Code**::
    
        # -*- coding: UTF-8 -*-
        """tabContainer"""

        class GnrCustomWebPage(object):
            py_requires = "gnrcomponents/testhandler:TestHandlerFull"
            
            def test_1_basic(self, pane):
                """Basic tabs"""
                tc = pane.tabContainer(height='200px', selected='^.selected.tab')
                cp = tc.contentPane(title='first tab')
                cp.div("""A tabContainer with two contentPanes. The "title" attribute appears on tabs.
                          You find the tab selected in the datastore at the path specified in the
                          selected attribute (in this example, test/test_1_basic/selected/tab)""",
                          text_align='justify', margin='10px')
                tc.contentPane(title='Second tab').div('I\'m the second tab', font_size='.9em',
                                                       text_align='justify', margin='10px')
                                                       
    .. _tab_tabposition:

"tabPosition" example
---------------------

    * `tabContainer [tabPosition] <http://localhost:8080/webpage_elements/widgets/layout/tabcontainer/2>`_
    * **Description**: features of the *tabPosition* attribute
      
      .. note:: example elements' list:
                
                * **classes**: :ref:`gnrcustomwebpage`
                * **components**: :ref:`testhandlerfull`
                * **webpage variables**: :ref:`webpages_py_requires`
                * **widgets**: :ref:`bordercontainer`, :ref:`contentpane`
                  
    * **Code**::
    
        # -*- coding: UTF-8 -*-
        """tabContainer - tabPosition"""
        
        class GnrCustomWebPage(object):
            py_requires = "gnrcomponents/testhandler:TestHandlerFull"
            
            def test_2_tabPosition(self, pane):
                """tabPosition attribute"""
                bc = pane.borderContainer(height='460px')
                tc = bc.tabContainer(height='100px', margin='1em', tabPosition='top-h')
                tc.contentPane(title='One').div("""tabPosition=\'top-h\' (this is the default
                                                   value for the tabPosition.)""", margin='1em')
                tc.contentPane(title='Two')
                tc = bc.tabContainer(height='100px', margin='1em', tabPosition='left-h')
                tc.contentPane(title='One').div('tabPosition=\'left-h\'', margin='1em')
                tc.contentPane(title='Two')
                tc = bc.tabContainer(height='100px', margin='1em', tabPosition='right-h')
                tc.contentPane(title='One').div('tabPosition=\'right-h\'', margin='1em')
                tc.contentPane(title='Two')
                tc = bc.tabContainer(height='100px', tabPosition='bottom')
                tc.contentPane(title='One').div('tabPosition=\'bottom\'', margin='1em')
                tc.contentPane(title='Two')
                
    .. _tab_remote:

"remote" example
------------------

    * `tabContainer [remote] <http://localhost:8080/webpage_elements/widgets/layout/tabcontainer/3>`_
    * **Description**: a tabContainer created remotely through the :ref:`remote` method (the :ref:`numberspinner`
      widget is used to choose the number of tabs)
      
      .. note:: example elements' list:
                
                * **classes**: :ref:`gnrcustomwebpage`
                * **components**: :ref:`testhandlerfull`
                * **controllers**: :ref:`remote`
                * **webpage variables**: :ref:`webpages_py_requires`
                * **widgets**: :ref:`bordercontainer`, :ref:`contentpane`, :ref:`data`,
                  :ref:`numberspinner`
      
    * **Code**::
    
        # -*- coding: UTF-8 -*-
        """tabContainer - remote"""

        class GnrCustomWebPage(object):
            py_requires = "gnrcomponents/testhandler:TestHandlerFull"
            
            def test_3_remote(self, pane):
                """remote tabContainer"""
                bc = pane.borderContainer(height='300px')
                fb = bc.contentPane(region='top', height='30px').formbuilder(cols=2)
                fb.numberspinner(value='^.numtabs', lbl='Number of tabs', min=0, max=20)
                bc.data('.numtabs', 0)
                fb.div('Move focus out of the NumberSpinner to update tabs (max tab numbers set to 20)',
                       font_size='.9em', text_align='justify', margin='10px')
                tc = bc.tabContainer(region='center')
                tc.remote('tabs', numtabs='^.numtabs')

            def remote_tabs(self, tc, numtabs):
                for i in range(numtabs):
                    tab = tc.contentPane(title='Tab %d' % i, position='absolute', margin='60px')
                    tab.div('This is tab n.%d' % i)