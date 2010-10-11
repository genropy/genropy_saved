	.. _common-dbtable:

=========
 Dbtable
=========
	
	The ``dbtable`` attribute is used to specify a path for a database :ref:`database-table` during a user query.
	
	The syntax is ``packageName.tableName.attributeName``, where:
	
		* ``packageName`` is the name of the package on which you're working;
		* ``tableName`` is the name of the :ref:`database-table` on which is executed the user query.

	Based on the form widget you're using, there is a different usage of ``dbtable``:
	
		* :ref:`dbtable-formbuilder-field`
		* :ref:`dbtable-dbselect-dbcombobox`
		
	.. _dbtable-formbuilder-field:

dbtable for the formbuilder and the field widgets
=================================================

	Please check the :ref:`form-field` page for all the details.

	.. _dbtable-dbselect-dbcombobox:

dbtable for the dbSelect and the dbCombobox widgets
===================================================

	In the dbSelect and in the dbCombobox you have to set the ``dbtable`` in this way::
	
		class GnrCustomWebPage(object):
			def main(self,root,**kwargs):
				fb = root.formbuilder(datapath='test1')
				fb.dbSelect('showcase.cast',rowcaption='$name',
				             value='^.person_id',lbl='Star')
				
				fb.dbCombobox('???',rowcaption=???)
				
	In this example, the first ``dbSelect`` attribute (its query-path) has the syntax ``packageName.tableName``. 
	
	The path of field value will be ``/test1/person_id/ID``, where ``test1`` is the name we chose for the datapath, ``person_id`` is the name of the attribute we chose for user query contained in the database model called ``cast`` and the ID is the record ID.
	