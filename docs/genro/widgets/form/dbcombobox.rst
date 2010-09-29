============
 DbCombobox
============

.. currentmodule:: form

.. class:: dbCombobox -  Genropy dbCombobox

	- :ref:`main-definition`
	
	- :ref:`where-is-it-?`
	
	- :ref:`A-brief-description`
	
	- :ref:`some-examples`
	
	- :ref:`main-attributes`
	
	- :ref:`other-features`
	
		- ???:ref:`first-reference`
		- ???:ref:`second-reference`

	.. _main-definition:

Definition
==========
		
	Here we report ???'s definition::
		
		def formbuilder(self, cols=1, dbtable=None, tblclass='formbuilder',
	                    lblclass='gnrfieldlabel', lblpos='L', _class='', fieldclass='gnrfield',
	                    lblalign=None, lblvalign='middle',
	                    fldalign=None, fldvalign='middle', disabled=False,
	                    rowdatapath=None, head_rows=None, **kwargs):

	.. _where-is-it-?:

Where
=====

	You can find ??? in *genro/gnrpy/???*

	.. _A-brief-description:

Description
===========

	???

	.. _some-examples:

Examples
========

	Let's see a code example::
	
		class GnrCustomWebPage(object):
			def main(self,root,**kwargs):
				fb=pane.formbuilder(datapath='test1',cols=2)
				???

	Let's see its graphical result:

	.. figure:: ???.png

	.. _main-attributes:

Attributes
==========

	+--------------------+-------------------------------------------------+--------------------------+
	|   Attribute        |          Description                            |   Default                |
	+====================+=================================================+==========================+
	| ``datapath``       | Set path for data.                              |  ``None``                |
	|                    | For more details, see :doc:`/common/datapath`   |                          |
	+--------------------+-------------------------------------------------+--------------------------+
	| ``disabled``       | If True, user can't act on the ???.             |  ``False``               |
	|                    | For more details, see :doc:`/common/disabled`   |                          |
	+--------------------+-------------------------------------------------+--------------------------+
	| ``hidden``         | Hide the ???.                                   |  ``False``               |
	|                    | See :doc:`/common/hidden`                       |                          |
	+--------------------+-------------------------------------------------+--------------------------+
	| ``label``          | Set ??? label.                                  |  ``None``                |
	|                    | For more details, see :doc:`/common/label`      |                          |
	+--------------------+-------------------------------------------------+--------------------------+
	| ``value``          | Set a path for ???'s values.                    |  ``None``                |
	|                    | For more details, see :doc:`/common/datastore`  |                          |
	+--------------------+-------------------------------------------------+--------------------------+

	.. _other-features:

Other features:
==============

	.. _first-reference:
	
??? Title first reference
=======================
	
	???
	
	.. _second-reference:
	
??? Title second reference
=======================
	
	???