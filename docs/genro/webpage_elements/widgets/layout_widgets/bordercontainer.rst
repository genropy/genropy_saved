.. _bordercontainer:

===============
BorderContainer
===============
    
    *Last page update*: |today|
    
    .. note:: BorderContainer features:
              
              * **Type**: :ref:`Dojo-improved widget <dojo_improved_widgets>`
              * **Common attributes**: check the :ref:`attributes_index` section
              
    .. note:: in Genro you can use the Dojo BorderContainer or the :ref:`framepane`, that
              is the Genro enhancement of the BorderContainer
    
    * :ref:`border_def`
    * :ref:`border_attributes`
    * :ref:`border_examples`:
    
        * :ref:`border_examples_simple`
        * :ref:`border_splitter`
        
.. _border_def:

definition
==========
    
    .. method:: pane.borderContainer([**kwargs])
    
    The borderContainer is a container partitioned into up to five regions: left (or leading),
    right (or trailing), top, and bottom with a mandatory center to fill in any remaining space.
    Each edge region may have an optional splitter user interface for manual resizing.
    
    In order to define a borderContainer you have to define at least one :ref:`contentpane`
    as a borderContainer child. This contentPane must include the ``region='center'`` attribute::
    
        def GnrCustomWebPage(self, root, **kwargs):
            bc = root.borderContainer(height='200px')
            bc.contentPane(region='center')
            
    Optionally, you can add other contentPanes with the other regions: left, right, top, bottom
    
.. _border_attributes:

attributes
==========
    
    **borderContainer's attributes**:
    
    * *design*: Dojo attribute. Define the layout of the element. For more information,
      check the :ref:`design` page. Default value is ``headline``
      
    **attributes of the borderContainer's children**:
    
    * *region*: Dojo attribute. Specify the spatial region occupied by the children.
      The center region is mandatory. The others regions are "left", "right", "top",
      "bottom". For more information, check the :ref:`border_examples_simple`
    * *splitter*: Dojo attribute. Boolean. If ``True``, user can modify the width of
      the paneContainer. For more information, check the :ref:`border_splitter`
      
      .. note:: The *splitter* attribute is NOT supported by the center region
                (that is, you cannot apply ``splitter=True`` on a contentPane
                including ``region='center'``)
                
.. _border_examples:

examples
========

.. _border_examples_simple:

simple example
--------------

    * `borderContainer [basic] <http://localhost:8080/webpage_elements/widgets/layout/bordercontainer/1>`_
    * **Description**:
    
      #. On "region" attribute:
      
         * "height" is mandatory in containers with ``region='top'`` and ``region='bottom'``
         * "width" is mandatory in containers with ``region='left'`` and ``region='right'``
         * you mustn't define any height/width in container with ``region='center'`` 
         
      #. "height" and "width" attributes support:
      
         * px (e.g: ``200px``)
         * em (e.g: ``4em``)
         * a percent number (e.g: ``width='20%'``)
         
      .. note:: example elements' list:
                
                * **classes**: :ref:`gnrcustomwebpage`
                * **components**: :ref:`testhandlerfull`
                * **webpage variables**: :ref:`webpages_py_requires`
                * **widgets**: :ref:`contentpane`
                
    * **Code**::
    
        # -*- coding: UTF-8 -*-
        """BorderContainer"""

        class GnrCustomWebPage(object):
            py_requires = "gnrcomponents/testhandler:TestHandlerFull"
            
            def test_1_basic(self, pane):
                """Basic example"""
                bc = pane.borderContainer(height='400px')
                top = bc.contentPane(region='top', height='5em', background_color='#98C5EA')
                top.div('\"height\" attribute is mandatory on the \"top\" region',
                         margin='10px', text_align='center')
                center = bc.contentPane(region='center', background_color='#E1E9E9', padding='10px')
                center.div("""Like in Dojo, this widget is a container partitioned into up to five regions:
                           left (or leading), right (or trailing), top, and bottom with a mandatory center
                           to fill in any remaining space. Each edge region may have an optional splitter
                           user interface for manual resizing.""",
                           text_align='justify', margin='10px')
                center.div("""Sizes are specified for the edge regions in pixels or percentage using CSS – height
                           to top and bottom, width for the sides. You have to specify the "height" attribute
                           for the "top" and the "bottom" regions, and the "width" attribute for the "left" and
                           "right" regions. You shouldn’t set the size of the center pane, since it’s size is determined
                           from whatever is left over after placing the left/right/top/bottom panes.)""",
                           text_align='justify', margin='10px')
                left = bc.contentPane(region='left', width='130px', background_color='#FFF25D', splitter=True)
                left.div('\"width\" attribute is mandatory on the \"left\" region', margin='10px')
                right = bc.contentPane(region='right', width='15%', background_color='#FFF25D')
                right.div('\"width\" attribute is mandatory on the \"right\" region', margin='10px')
                bottom = bc.contentPane(region='bottom', height='20%', background_color='#98C5EA')
                bottom.div('\"height\" attribute is mandatory on the \"bottom\" region',
                            margin='10px', text_align='center')
                            
    .. _border_splitter:

splitter example
----------------

    * `borderContainer [splitter] <http://localhost:8080/webpage_elements/widgets/layout/bordercontainer/2>`_
    * **Description**: "splitter" attribute example
    
      .. note:: example elements' list:
                
                * **classes**: :ref:`gnrcustomwebpage`
                * **components**: :ref:`testhandlerfull`
                * **webpage variables**: :ref:`webpages_py_requires`
                * **widgets**: :ref:`contentpane`
                
    * **Code**::
    
        # -*- coding: UTF-8 -*-
        """BorderContainer"""

        class GnrCustomWebPage(object):
            py_requires = "gnrcomponents/testhandler:TestHandlerFull"
            
            def test_2_splitter(self, pane):
                """splitter example"""
                ta = 'center'
                m = '15px'
                bc = pane.borderContainer(height='400px')
                top = bc.contentPane(region='top',height='5em',splitter=True)
                top.div('I\'m top', text_align=ta, margin=m)
                left = bc.contentPane(region='left',width='20%',splitter=True)
                left.div('I\'m left', text_align=ta, margin=m)
                right = bc.contentPane(region='right',width='80px',splitter=True)
                right.div('I\'m right', text_align=ta, margin=m)
                bottom = bc.contentPane(region='bottom',height='80px',splitter=True)
                bottom.div('I\'m bottom', text_align=ta, margin=m)
                center = bc.contentPane(region='center',padding='10px')
                center.div('I\'m center (you cannot give me \"splitter\" attribute)', text_align=ta, margin=m)
                