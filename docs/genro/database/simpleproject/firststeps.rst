.. _genro_simple_firststeps:

===================
METTERE UN TITOLONE
===================

	* :ref:`simple_build_package`

.. _simple_build_package:

Creation of a package
=====================

	You have to create a package for your database management. We suggest you to create your package with the same name of your project (it isn't mandatory).
	
	To create a package, go inside the package folder (``../projectname/packages``) and write this command line::
	
		gnrmkpackage packagename
		
	In our example we'll type ``gnrmkpackage myproject`` at the path: ``../myproject/packages``.
	
	If you want to call an help for package creation options, type ``gnrmkpackage -h``::
	
		Usage: gnrmkpackage [options]
		
		Options:
		  -h, --help            show this help message and exit
		  -b BASE_PATH, --base-path=BASE_PATH
		                        base path where project will be created
	
	Now your ``packages`` folder should be like this one:
	
	.. image:: ../../images/simpleproject/simpleproject-package.png
	
	