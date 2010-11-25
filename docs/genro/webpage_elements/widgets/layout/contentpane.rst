	.. _genro-contentpane:

==============
 content pane
==============

	- :ref:`cp-definition`

	- :ref:`cp-examples`: :ref:`cp-simple`

	- :ref:`cp_common_attributes`

	.. _cp-definition:

Definition
==========

	A contentPane_ is a Dojo widget that can be used as a standalone widget or as a baseclass for other widgets. Don’t confuse it with an iframe, it only needs/wants document fragments.
	
	.. _contentPane: http://api.dojotoolkit.org/jsdoc/1.2/dijit.layout.ContentPane

	.. _cp-examples:

Examples
========

	.. _cp-simple:

Simple example
==============

Here we show you a simple example of a ``contentPane``::

	class GnrCustomWebPage(object):
		def main(self,root,**kwargs):
			bc = root.borderContainer(height='400px')
			top = bc.contentPane(region='top',height='5em',background_color='#f2c922')
			top.div('Specify my height!',font_size='.9em',text_align='justify',margin='10px')
			center = bc.contentPane(region='center',background_color='silver',padding='10px')
			center.div("""Like in Dojo, this widget is a container partitioned into up to five regions:
			              left (or leading), right (or trailing), top, and bottom with a mandatory center
			              to fill in any remaining space. Each edge region may have an optional splitter
			              user interface for manual resizing.""",
			              font_size='.9em',text_align='justify',margin='10px')
			center.div("""Sizes are specified for the edge regions in pixels or percentage using CSS – height
			              to top and bottom, width for the sides. You have to specify the "height" attribute
			              for the "top" and the "bottom" regions, and the "width" attribute for the "left" and
			              "right" regions. You shouldn’t set the size of the center pane, since it’s size is determined
			              from whatever is left over after placing the left/right/top/bottom panes.)""",
			              font_size='.9em',text_align='justify',margin='10px')
			left = bc.contentPane(region='left',width='130px',background_color='red',splitter=True)
			left.div('Specify my width!',font_size='.9em',text_align='justify',margin='10px')
			right = bc.contentPane(region='right',width='130px',background_color='yellow')
			right.div('Specify my width!',font_size='.9em',text_align='justify',margin='10px')
			bottom = bc.contentPane(region='bottom',height='80px',background_color='grey')
			bottom.div('Specify my height!',font_size='.9em',text_align='justify',margin='10px')

.. #NISO ??? Add a demo!

.. _cp_common_attributes:

Common attributes
=================

	For common attributes, see :ref:`genro-layout-common-attributes`.
	