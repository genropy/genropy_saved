	.. _common-datapath:

==========
 Datapath
==========

	- :ref:`data-description`

	- :ref:`data-validity`

	- :ref:`data-examples`
	
		- :ref:`bc-example`
		
		- :ref:`absolute-example`

	.. _data-description:

Datapath description
====================

	Datapath is an attribute used to create a hierarchy of your data's addresses into the :ref:`genro-datastore`.
	
	You have to use ``datapath`` to an object that you want to be the father, while on the son elements you have to specify their relative path (but you can also specify an absolute path).
	
	Let's see the syntax for an absolute path and for a relative path:
	
	* ``pathAbsoluteInDatastore``: with this syntax your data will be saved in its absolute path.
	
	* ``.pathRelativeInDatastore``: with this syntax your path will be relative. Pay attention that you can use this attribute only for a son object, that is only for an object that is linked to a father on which it is defined the "datapath" attribute. Every dot "." that you use have the meaning of a new subfolder; so::
	
		class GnrCustomWebPage(object):
			def main(self,root,**kwargs):
				bc = root.borderContainer(datapath='test1')
				bc.numberTextbox(value='^.number1')
				bc.numberTextbox(value='^number2')
				bc.numberTextbox(value='^.number.number3')
	
	The first numberTextbox will have the following path: ``test1/number1`` (this is a relative path). The second one will have the following path: ``number2`` (that is an absolute path!). The third one will have the following path: ``test1/number/number3``. See more explanations in the :ref:`data-examples` section.

	.. _data-validity:

Datapath validity
=================

	You can give "datapath" attribute to each object, but it is useful give this attribute only to the objects that contain other objects (so give this attribute to container objects).

	.. _data-examples:

Examples
========

	.. _bc-example:

A simple example
================

	In the first example we apply datapath to a bordercontainer: the result is that every bordercontainer son CAN link its values to the datapath. So if we write::

		class GnrCustomWebPage(object):
			def main(self,root,**kwargs):
				bc = root.borderContainer(datapath='test1')
				fb = formbuilder(cols=2)
				fb.textbox(value='^.name',lbl='Name')
				fb.textbox(value='^.surname',lbl='Surname')
				
	the strings typed in the textbox will be saved in the following paths: ``test1/name``, ``test1/surname``

	.. _absolute-example:

Absolute path example
=====================
	
	We report quite the same code of example one (the difference is little but involves a big change!)::

		class GnrCustomWebPage(object):
			def main(self,root,**kwargs):
				bc = root.borderContainer(datapath='test2')
				fb = formbuilder(cols=2)
				fb.textbox(value='^.name',lbl='Name')
				fb.textbox(value='^surname',lbl='Surname')
				
	In this case the path of textboxes are: ``test2/name`` and ``surname``, so using ``value`` attribute without the dot allow you to create an absolute path.
	