=========
 Dbtable
=========
	
	The ``dbtable`` attribute is used to specify a path of a database table for the user queries. If you don't specify it, Genro will use as dbtable value the value of the :doc:`/database/maintable`. Let's see two examples on ``maintable``, and two examples on ``dbtable``::
				
		# EXAMPLE 1
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
				
		# EXAMPLE 2
		class GnrCustomWebPage(object):
			# Here we haven't written the maintable, and so...
			
			def main(self,root,**kwargs):
				fb = root.formbuilder(cols=2)
				fb.field('packageName.fileName.attribute') # ... this is the only way to recall database.
				fb.field('attribute')                      # This line will not work!
	
	Now let's see the two examples on dbtable::
				
		# EXAMPLE 3
		class GnrCustomWebPage(object):
			# Here we haven't written the maintable...
			
			def main(self,root,**kwargs):
				fb = root.formbuilder(cols=2)
				fb.field('attribute',dbtable='packageName.fileName') # ... but this line works, even if you
				                                                     # haven't specified the maintable!
		# EXAMPLE 4
		class GnrCustomWebPage(object):
			maintable='shop_management.storage' # Like before, "shop_management" is the package name, while
			                                    # "storage.py" is the file name where lies database.
			
			def main(self,root,**kwargs):
				fb = root.formbuilder(cols=2)
				fb.field('name') # This field will get "name" attribute from the "shop_management" package,
				                 # in the file named "storage".
				fb.field('name',dbtable='sell_package.employees') # This field will get "name" attribute from
				                                                  # the "sell_package" package, in the file
				                                                  # named "employees.py".
				