.. _genro_layout_introduction:

================================
 Introduction to the containers
================================

	In Genro you can use layout containers to put panes (or other containers) in specific regions of your page.
	
	There are five regions: top, left, right, bottom and a mandatory center.

	As we previously said [#]_, Genro inherit its forms (containers and panes) directly from Dojo.

	The containers are:
	
	- the :ref:`genro_bordercontainer`;
	
	- the :ref:`genro-contentpane`;
	
	- the :ref:`genro-accordioncontainer`;
	
	- the :ref:`genro-stackcontainer`;
	
	- the :ref:`genro_tabcontainer`.
	
	Every container has its children (that are contentPanes). For example, in the accordionContainer you have the accordionPanes.
	
	.. _genro-layout-common-attributes:

Common attributes
=================

	There are some common attributes that you can use with all the containers and panes:
	
	* ``datapath``: set the root's path of data. Default value is ``None``. For more details, check the :ref:`genro_datapath` page
	* ``disabled``: if True, disable the container/pane. Default value is ``False``. For more information, check the :ref:`genro-disabled` documentation page
	* ``height``: Set the height of the container. MANDATORY if the container is the father container (example: height='100px')
	* ``hidden``: if True, allow to hide this widget. Default value is ``False``. For more information, check the :ref:`genro-hidden` documentation page

**Footnotes**

.. [#] We have introduced the containers in the :ref:`genro_webpage-elements-introduction` page.