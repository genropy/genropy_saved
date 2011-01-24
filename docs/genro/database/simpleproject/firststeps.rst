.. _genro_simpleproject_firststeps:

===========
First steps
===========

	You have to create a package for your database management. We suggest you to create the first package with the same name of your project (itsn't mandatory, however).
	
	To create a package, go inside the package folder (``../projectname/package``) and write this command line::
	
		gnrmkpackage packagename
	
	To call an help for the options of the package creation, type ``gnrmkpackage -h``::
	
		Usage: gnrmkpackage [options]
		
		Options:
		  -h, --help            show this help message and exit
		  -b BASE_PATH, --base-path=BASE_PATH
		                        base path where project will be created
	
	
	???
	Model --> containing database :ref:`genro_database_table`
	Webpages --> containing all the webpages of your project --> :ref:`genro_webpage`