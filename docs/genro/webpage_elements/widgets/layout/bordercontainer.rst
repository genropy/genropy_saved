	.. _genro-bordercontainer:

==================
 Border container
==================

	- :ref:`border-definition`

	- :ref:`border-examples`: :ref:`border-simple`

	- :ref:`border_attributes`

	- :ref:`border-common-attributes`
	
	- attributes explanation: :ref:`border-regions`, :ref:`border_splitter`

	.. _border-definition:

Definition
==========

	The border container inherit its properties from Dojo BorderContainer_. It is a container partitioned into up to five regions: left (or leading), right (or trailing), top, and bottom with a mandatory center to fill in any remaining space. Each edge region may have an optional splitter user interface for manual resizing.

	.. _BorderContainer: http://docs.dojocampus.org/dijit/layout/BorderContainer

	.. _border-examples:

Examples
========

	.. _border-simple:

Simple example
==============

	Here we show you a simple code containing a ``border container``::

		class GnrCustomWebPage(object):
			def main(self,root,**kwargs):
				bc = pane.borderContainer(height='400px')
				top = bc.contentPane(region='top',height='5em',background_color='#f2c922')
				left = bc.contentPane(region='left',width='100px',background_color='red',splitter=True)
				right = bc.contentPane(region='right',width='80px',background_color='yellow')
				bottom = bc.contentPane(region='bottom',height='80px',background_color='grey')
				center = bc.contentPane(region='center',background_color='silver',padding='10px')

.. #NISO ??? Add a demo!

.. _border_attributes:

Attributes
==========

	+--------------------+----------------------------------------------------+--------------------------+
	|   Attribute        |          Description                               |   Default                |
	+====================+====================================================+==========================+
	| ``regions``        | borderContainer's attribute. Allow to act on       |  ``None``                |
	|                    | regions. Check the :ref:`border-regions` example   |                          |
	+--------------------+----------------------------------------------------+--------------------------+
	| ``splitter``       | borderContainer's children attribute.              |  ``False``               |
	|                    | If true, it allows to modify the region width.     |                          |
	|                    | For more information, check :ref:`border_splitter` |                          |
	|                    | page                                               |                          |
	+--------------------+----------------------------------------------------+--------------------------+

	.. _border-common-attributes:

Common attributes
=================

	For common attributes, see :ref:`genro-layout-common-attributes`

	.. _border-regions:

Regions attribute
=================

	With the "regions" attribute you can act on the regions of the borderContainer's children. You can modify their dimensions, and see them in the :ref:`genro-datastore`.
	
	The syntax is: ``regions='folderName'``.
	If you have to interact with the regions, the syntax is: ``folderName.regionName``; so, if you have to interact with the "left" region, you have to write: ``folderName.left``.
	
	In this example, we give the name "regions" as folder name of the ``regions`` attribute::
	
		bc = borderContainer(regions='^regions')
	
	You can modify their dimensions for example with :ref:`genro-data`,
	
	::
		
		root.data('regions.left?show',False)
		root.data('regions.top',show=False)
		
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

.. ??? Add online demo! #NISO

.. _border_splitter:

Splitter attribute
==================

	Here we show you an example for the ``splitter`` attribute::

		class GnrCustomWebPage(object):
			def main(self,root,**kwargs):
				bc = pane.borderContainer(height='400px')
				top = bc.contentPane(region='top',height='5em',background_color='#f2c922',splitter=True)
				left = bc.contentPane(region='left',width='100px',background_color='red',splitter=True)
				right = bc.contentPane(region='right',width='80px',background_color='yellow',splitter=True)
				bottom = bc.contentPane(region='bottom',height='80px',background_color='grey',splitter=True)
				center = bc.contentPane(region='center',background_color='silver',padding='10px')

	The ``splitter`` attribute is NOT supported by the center region (that is, you cannot apply ``splitter=True`` on a contentPane including ``region='center'``).

.. #NISO ??? Add a demo!
