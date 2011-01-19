	.. _genro-data:

====
data
====

	- :ref:`data_def`
	
	- :ref:`data_attr`
	
	- :ref:`data_examples`

.. _data_def:

Definition
==========

	The ``data`` is a server-side Genro controller that allows to define variables from server to client.

	.. method:: pane.data([*args[, **kwargs]])

	*Where*:

		* ``args[0]`` includes the path of the value.
		* ``args[1]`` includes the value.
		* in the ``**kwargs`` you can insert the ``_serverpath`` attribute

.. _data_attr:

Attributes
==========

	**data attributes**:

	* ``_serverpath``: allow to keep updated data both on the server and in the client. For more information, check ???
	
	**common attributes**:
	
		For common attributes (``_init``, ``_onStart``, ``_timing``) see controllers' :ref:`controllers_attributes`

.. _data_examples:

Examples
========

	Example::
	
		class GnrCustomWebPage(object):
			def main(self,root,**kwargs):
				root.data('icon','icnBaseOk')
				root.data('fontType','Courier')
				root.data('widthButton','10em')
				root.data('fontSize','22px')
				root.data('color','green')
				bc = root.borderContainer()
				bc.button('Click me',iconClass='^icon',width='^widthButton',color='^color',
				           font_size='^fontSize',font_family='^fontType',action="alert('Clicked!')")
