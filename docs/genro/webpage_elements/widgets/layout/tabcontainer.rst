.. _genro_tabcontainer:

============
tabContainer
============

    * :ref:`tab_definition`
    * :ref:`tab_attributes`
    * :ref:`tab_examples`
    
    * attributes explanation: :ref:`tab_selected`, :ref:`tab_tabposition`

.. _tab_definition:

Definition
==========

    .. method:: pane.tabContainer([**kwargs])

    A TabContainer is a container that has multiple panes, but shows only one pane at a time. There are a set of tabs corresponding to each pane, where each tab has the title of the pane.

.. _tab_attributes:

Attributes
==========

    **tabContainer's attributes**:
    
    * *tabPosition*: define the place of the paneContainer's labels. Default value is ``top-h``. For all supported possibilities, check the :ref:`tab_tabposition` example

    * *selected*: Allow to visualize in the :ref:`genro_datastore` the current selected tab as a type-number into a specific folder. Default value is ``None``. Check the :ref:`tab_selected` example for more informations.

    **attributes of the tabContainer's children (paneContainers)**:
    
        There aren't particular attributes.

    **common attributes**:

        For common attributes, see :ref:`genro_layout_common_attributes`

.. _tab_examples:

Examples
========

.. _tab_simple:

**Simple example:** Here we show you a simple example of a ``tabContainer``::

    class GnrCustomWebPage(object):
        def main(self,root,**kwargs):
            tc = pane.tabContainer(height='200px')
            cp = tc.contentPane(title='title place',iconClass='icnBaseAction')
            tc.contentPane(title='Second tab').button('Dummy button (no action)',margin='10px')

.. _tab_selected:

"selected" attribute
====================

    With the *selected* attribute Genro create a folder path in the :ref:`genro_datastore` where lies a number indicating the tab selected (for the first tab you'll find 0, for the second one 1 and so on).
    
    The syntax is ``selected='folderPathName'``
    
    Example::
    
        selected='^selected.tab'
        
    The *selected* of this example will create the following path folder: ``/selected/tab``

.. _tab_tabposition:

"tabPosition" attribute
=======================

    In the following example we show you all the possibilities for the *tabPosition* attribute::

        class GnrCustomWebPage(object):
            def main(self,root,**kwargs):
                bc = pane.borderContainer(height='460px')
                tc = bc.tabContainer(height='100px',margin='1em',tabPosition='top-h')
                tc.contentPane(title='One').div("""tabPosition=\'top-h\' (this is the default
                                                   value for the tabPosition.)""",margin='1em')
                tc.contentPane(title='Two')
                tc = bc.tabContainer(height='100px',margin='1em',tabPosition='left-h')
                tc.contentPane(title='One').div('tabPosition=\'left-h\'',margin='1em')
                tc.contentPane(title='Two')
                tc = bc.tabContainer(height='100px',margin='1em',tabPosition='right-h')
                tc.contentPane(title='One').div('tabPosition=\'right-h\'',margin='1em')
                tc.contentPane(title='Two')
                tc = bc.tabContainer(height='100px',tabPosition='bottom')
                tc.contentPane(title='One').div('tabPosition=\'bottom\'',margin='1em')
                tc.contentPane(title='Two')
                