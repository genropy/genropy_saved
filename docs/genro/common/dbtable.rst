	.. _common-dbtable:

=========
 Dbtable
=========
	
	The ``dbtable`` attribute is used to specify a path for a database :ref:`database-table` during a user query.
	
	The sintax is ``packageName.tableName``, where:
	
		* ``packageName`` is the name of the package on which you're working;
		* ``tableName`` is the name of the :ref:`database-table` on which is executed the user query.

	Based on the form widget you're using, there is a different usage of ``dbtable``:
	
		* :ref:`dbtable-formbuilder-field`
		* :ref:`dbtable-dbselect-dbcombobox`
		
	.. _dbtable-formbuilder-field:

dbtable for the formbuilder and the field widgets
=================================================

	???

	.. _dbtable-dbselect-dbcombobox:

dbtable for the dbSelect and the dbCombobox widgets
===================================================

	???
	
	
	
	
	
	
	
	
	
	
	
	
	If you don't specify it, Genro will use as dbtable value the :ref:`database-maintable` value.
	
	
	
	Let's see two examples about the :ref:`database-maintable`, and two examples about the ``dbtable``.
	
	Maintable examples::
				
		# maintable - EXAMPLE 1
		class GnrCustomWebPage(object):
			maintable='packageName.fileName'    # This is the line for maintable definition, whereas "packageName"
			                                    # is the name of the package, while "fileName" is the name of the
			                                    # model file, where lies the database.
			
			def main(self,root,**kwargs):
				fb = root.formbuilder(cols=2)
				
				# For specifing "maintable", you can write one of the following two lines,
				# because they have the same meaning.
				fb.field('packageName.fileName.attribute')
				fb.field('attribute')
				
		# maintable - EXAMPLE 2
		class GnrCustomWebPage(object):
			# Here we haven't written the maintable, and so...
			
			def main(self,root,**kwargs):
				fb = root.formbuilder(cols=2)
				fb.field('packageName.fileName.attribute') # ... this is the only way to recall database.
				fb.field('attribute')                      # This line will not work!
	
	dbtable examples::
				
		# dbtable - EXAMPLE 1
		class GnrCustomWebPage(object):
			# Here we haven't written the maintable...
			
			def main(self,root,**kwargs):
				fb = root.formbuilder(cols=2)
				fb.field('attribute',dbtable='packageName.fileName') # ... but this line works, even if you
				                                                     #     haven't specified the maintable!
		# dbtable - EXAMPLE 2
		class GnrCustomWebPage(object):
			maintable='shop_management.storage' # Like before, "shop_management" is the package name, while
			                                    #     "storage.py" is the file name where lies database.
			
			def main(self,root,**kwargs):
				fb = root.formbuilder(cols=2)
				fb.field('name') # This field will get "name" attribute from the "shop_management" package,
				                 # in the file named "storage".
				fb.field('name',dbtable='sell_package.employees') # This field will get "name" attribute from
				                                                  #      the "sell_package" package, in the file
				                                                  #      named "employees.py".
				