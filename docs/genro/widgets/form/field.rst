	.. _form-field:

=======
 Field
=======

.. currentmodule:: form

.. class:: Field -  Genropy Field

	- :ref:`field-definition`

	- :ref:`field-where`

	- :ref:`field-description-examples`

		- :ref:`first-one`
		- :ref:`second-one`
		- :ref:`third-one`

	- :ref:`field-attributes`
	
	- :ref:`field-other-attributes`

	.. _field-definition:

Definition
==========

	Here we report Field's definition::

		def nameOfObject(args): #NISO ??

	.. _field-where:

Where
=====

	You can find Field in *genro/gnrpy/...* #NISO ??

	.. _field-description-examples:

Description and Examples
========================

	``Field`` is used to view and select data included in a database :ref:`database-table` (and, eventually, through the ``zoom`` attribute, is used to modify them).

	Its type is inherited from the type of data contained in the table to which ``Field`` refers. For example, if ``Field`` catches data from a :ref:`textboxes-numbertextbox`, its type is actually a ``numberTextbox``.

	``Field`` MUST be a son of the form widget called :ref:`form-formbuilder`, and ``formbuilder`` itself MUST have a :ref:`common-datapath` for inner relative path gears. So, ``Field`` search a form to bind itself to (so don't forget to link every ``Field`` to a ``formbuilder``!).
	
	The last thing is to specify the database table to which the Field refers to. There are three different possibilities for doing this, that are:
	
	* :ref:`first-one`
	* :ref:`second-one`
	* :ref:`third-one`
	
	.. _first-one:

dbtable on the formbuilder
==========================

	You can set the ``dbtable`` attribute on the formbuilder, like::
	
		class GnrCustomWebPage(object):
			def main(self,root,**kwargs):
				fb = root.formbuilder(datapath='test1',dbtable='showcase.cast')
				
	where ``showcase`` is the name of the package and ``cast`` is the name of the ``table``. At this point, the field will be like::
	
				fb.field('person_id',rowcaption='$name')

	So, the first value of the field contains the name of the attribute you want to save in the :ref:`datastore` (for rowcaption explanation, check :ref:`field-attributes`).

	.. _second-one:

maintable
=========

	In this example we show to you that you can introduce the ``maintable`` in the place of the ``formbuilder`` ``dbtable``::

		class GnrCustomWebPage(object):
		
			maintable='showcase.cast'
		
			def main(self,root,**kwargs):
				fb = root.formbuilder(datapath='test2')
				fb.field('person_id',rowcaption='$name')
	
	If you have more than one ``formbuilder``, the ``maintable`` is being applied to EVERY ``formbuilder``.
	
	.. _third-one:
	
internal dbtable
================

	In this last case we show that you can set the dbtable inside the field::
	
		class GnrCustomWebPage(object):
			def main(self,root,**kwargs):
				fb = root.formbuilder(datapath='test3')
				fb.field('showcase.cast.person_id',rowcaption='$name')
				
	In this example, the first ``Field`` attribute (its query-path) has the sintax ``packageName.tableName.tableAttributeName``. Genro trasforms the ``Field`` into a ``dbselect``, splitting the query-path in two: ``packageName.tableName`` will go as the string applied to the ``dbtable`` attribute, while the ``tableAttributeName`` will go as the string applied to the ``value`` attribute. So, the path of field value will be ``/test1/person_id/ID``, where ``test1`` is the name we chose for the datapath, ``person_id`` is the name of the attribute we chose for user query contained in the database model called ``cast`` and the ID is the record ID.

	.. _field-attributes:

Attributes
==========

	+--------------------+-------------------------------------------------+--------------------------+
	|   Attribute        |          Description                            |   Default                |
	+====================+=================================================+==========================+
	|  ``limit``         | The max number of rows displayed in a field as  |  ``10``                  |
	|                    | response to user request. The last line is      |                          |
	|                    | always a line with no characters, so user can   |                          |
	|                    | choose it to undo his request                   |                          |
	+--------------------+-------------------------------------------------+--------------------------+
	|  ``lbl``           | Set the Field label. Properly, "lbl" is a       |  name_long value         |
	|                    | formbuilder's son attribute, so if you don't    |                          |
	|                    | specify it, then Field will inherit it from the |                          |
	|                    | :ref:`name-name_long` attribute of the          |                          |
	|                    | requested data                                  |                          |
	+--------------------+-------------------------------------------------+--------------------------+
	|  nameOfTheColumn   | MANDATORY - The first field's parameter; it is  |  ``None``                |
	|                    | field's query path; its complete sintax is      |                          |
	|                    | ``packageName.tableName.tableAttributeName``.   |                          |
	|                    | It can be used in a combo with ``dbtable``      |                          |
	|                    | (a ``formbuilder`` attribute) and with the      |                          |
	|                    | ``maintable``                                   |                          |
	+--------------------+-------------------------------------------------+--------------------------+
	| ``rowcaption``     | Allow user to view records through              |  ``None``                |
	|                    | :ref:`name-name_long` value.                    |                          |
	|                    | Without ``rowcaption``, user will see value ID. |                          |
	|                    | Check for more information on                   |                          |
	|                    | :ref:`database-rowcaption` page                 |                          |
	+--------------------+-------------------------------------------------+--------------------------+
	| ``zoom``           | It allows to open the linked record in its      |  ``True``                |
	|                    | :ref:`database-table`. For further              |                          |
	|                    | details, check :ref:`components-standardtable`  |                          |
	+--------------------+-------------------------------------------------+--------------------------+
	
	.. _field-other-attributes:
	
Common attributes
=================

	+--------------------+-------------------------------------------------+--------------------------+
	|   Attribute        |          Description                            |   Default                |
	+====================+=================================================+==========================+
	| ``disabled``       | If True, user can't act on the dbselect.        |  ``False``               |
	|                    | For more details, see :ref:`common-disabled`    |                          |
	+--------------------+-------------------------------------------------+--------------------------+
	| ``hidden``         | Hide the dbselect.                              |  ``False``               |
	|                    | See :ref:`common-hidden`                        |                          |
	+--------------------+-------------------------------------------------+--------------------------+
	| ``value``          | Set a path for dbselect's values.               |  ``None``                |
	|                    | For more details, see :ref:`common-datapath`    |                          |
	+--------------------+-------------------------------------------------+--------------------------+
	
