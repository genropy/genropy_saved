.. _genro_bordercontainer:

===============
borderContainer
===============

    .. note:: The Genro borderContainer has been taken from Dojo without adding any modifies. In this page you will find some interesting features that we want to point up. For more information, check the Dojo's borderContainer documentation.
    
    * :ref:`border_def`
    * :ref:`border_attributes`
    * :ref:`border_examples`: :ref:`border_examples_simple`
    * :ref:`border_attr_exp`: :ref:`border_regions`, :ref:`border_splitter`
    
.. _border_def:

Definition
==========
    
    .. method:: pane.borderContainer([**kwargs])
    
    The borderContainer is a container partitioned into up to five regions: left (or leading), right (or trailing), top, and bottom with a mandatory center to fill in any remaining space. Each edge region may have an optional splitter user interface for manual resizing.
    
    In order to define a borderContainer you have to define at least one :ref:`genro_contentpane` as a borderContainer child. This contentPane must include the ``region='center'`` attribute::
    
        bc = root.borderContainer(height='200px')
        bc.contentPane(region='center')
        
    Optionally, you can add other contentPanes with the other regions: left, right, top, bottom. For more information, check the :ref:`border-simple` below.
    
.. _border_attributes:

Attributes
==========
    
    **borderContainer's attributes**:
    
    * *regions*: Allow to act on regions. For more information, check the :ref:`border_regions` example
    
    **attributes of the borderContainer's children (paneContainers)**:
    
    * *splitter*: If true, user can modify the width of the paneContainer. For more information,
      check :ref:`border_splitter` example
    
    **Common attributes**:
    
        For common attributes, see :ref:`genro_layout_common_attributes`
        
.. _border_examples:

Examples
========

.. _border_examples_simple:

simple example
--------------

    Here we show you a simple code containing a ``borderContainer``::
    
        class GnrCustomWebPage(object):
            def main(self,root,**kwargs):
                bc = root.borderContainer(height='400px')
                top = bc.contentPane(region='top',height='5em',background_color='#f2c922')
                left = bc.contentPane(region='left',width='100px',background_color='red',splitter=True)
                right = bc.contentPane(region='right',width='80px',background_color='yellow')
                bottom = bc.contentPane(region='bottom',height='80px',background_color='grey')
                center = bc.contentPane(region='center',background_color='silver',padding='10px')

.. _border_attr_exp:

Attributes explanation
======================

.. _border_regions:

*regions* attribute
-------------------

    With the *regions* attribute you can act on the regions of the borderContainer's children. You can modify
    their dimensions, and see them in the :ref:`genro_datastore`.
    
    The syntax is: ``regions='folderName'``.
    If you have to interact with the regions, the syntax is: ``folderName.regionName``; so, if you have to
    interact with the "left" region, you have to write: ``folderName.left``.
    
    In this example, we give the name "regions" as folder name of the *regions* attribute::
    
        bc = borderContainer(regions='^regions')
        
    You can modify their dimensions for example with :ref:`genro_data`::
        
        root.data('regions.left?show',False) # these two lines have the same meaning
        root.data('regions.left',show=False)
        
    or you can modify their dimensions with a Javascript line code::
    
        genro.setData('regions.left','150px')
        
    Let's see now a complete example::
        
        class GnrCustomWebPage(object):
            def main(self,root,**kwargs):
                root.data('regions.left?show',False)
                root.data('regions.top',show=False)
                
                bc = root.borderContainer(height='400px')
                top = bc.contentPane(region='top',height='70px')
                top.formbuilder(cols=2)
                top.div("""With the "regions" attribute you can add the "show" attribute
                           to the borderContainer and its regions.""",
                           colspan=2,background_color='#f2c922',margin_bottom='5px')
                top.checkbox(value='^regions.top?show',label='Show top pane')
                top.checkbox(value='^regions.left?show',label='Show left pane')
                
                bc2 = bc.borderContainer(region='center',regions='^regions')
                top2 = bc2.contentPane(region='top',height='5em',background_color='#f2c922')
                left2 = bc2.contentPane(region='left',width='100px',background_color='orange',splitter=True)
                center2 = bc2.contentPane(region='center',background_color='silver',padding='10px')
                center2.textbox(value='^regions.left',default='100px',margin_left='5px')
                center2.div("""In this sample there are two buttons that can make visible the left and the top
                               contentPane(s); in particular, the left pane had the attribute "splitter=True",
                               so you can move it; there's a textBox too where you can see the dimension
                               (in pixel) of the left pane (you can see its dimension only after the first move
                               you made on it).""")
                               
.. _border_splitter:

*splitter* attribute
--------------------

    Here we show you an example for the *splitter* attribute::
    
        class GnrCustomWebPage(object):
            def main(self,root,**kwargs):
                bc = pane.borderContainer(height='400px')
                top = bc.contentPane(region='top',height='5em',background_color='#f2c922',splitter=True)
                left = bc.contentPane(region='left',width='100px',background_color='red',splitter=True)
                right = bc.contentPane(region='right',width='80px',background_color='yellow',splitter=True)
                bottom = bc.contentPane(region='bottom',height='80px',background_color='grey',splitter=True)
                center = bc.contentPane(region='center',background_color='silver',padding='10px')
                
    .. note:: The *splitter* attribute is NOT supported by the center region (that is, you cannot apply ``splitter=True`` on a contentPane including ``region='center'``).
