.. _packages_main:

===========
``main.py``
===========

    .. image:: ../../images/projects/packages_main.png
    
    * :ref:`main_intro`
    * :ref:`main_autocreation`
    * :ref:`main_description`
    * :ref:`main_package_class`
    
        Package class methods:
        
        * :ref:`methods_config_attributes`
        * :ref:`methods_config_db`
        * :ref:`methods_custom_type`
        * :ref:`methods_loginUrl`
        * add??? link to methods!
    
    * :ref:`main_table_class`
    
        Table class methods:
        
        * add??? link to methods!
    
.. _main_intro:
    
introduction
============
    
    The ``main.py`` file allows to ... add???
    
.. _main_autocreation:

autocreation of the ``main.py``
===============================

    If you have followed the instruction of the :ref:`packages_autofill` section, the
    ``main.py`` will be filled with the following lines::
    
        #!/usr/bin/env python
        # encoding: utf-8
        from gnr.app.gnrdbo import GnrDboTable, GnrDboPackage, Table_counter, Table_userobject
        
        class Package(GnrDboPackage):
            def config_attributes(self):
                return dict(comment='base package',sqlschema='base',
                            name_short='Base', name_long='Base', name_full='Base')
                            
            def config_db(self, pkg):
                pass
                
            def loginUrl(self):
                return 'base/login'
                
        class Table(GnrDboTable):
            pass
            
    where the :ref:`methods_config_attributes` and the :ref:`methods_loginUrl` methods have
    been filled with the same name of the package (in this example the package is called ``base``).
    
    In the next section we describe all the features of the ``main.py`` file.
    
.. _main_description:
    
description
===========
    
    The first two lines define the encoding::
    
        #!/usr/bin/env python
        # -*- coding: utf-8 -*-
        
    (here we set the encoding to 'utf-8').
    
    The next line is written for the packages importation::
    
        from gnr.app.gnrdbo import GnrDboTable, GnrDboPackage, Table_counter, Table_userobject
    
    .. warning:: the importation of these four packages is MANDATORY for a correct use of
                 the ``main.py`` file.
                 
    In the ``main.py`` file you have many classes to customize your project:
    
    * the :ref:`main_package_class`
    * the :ref:`main_table_class`
    * the add???
    
.. _main_package_class:

Package class
=============
    
    .. class:: Package(GnrDboPackage)
    
    The ``Package`` class is used for ... add???
    
    We list now all the methods of the ``Package`` class:

.. _methods_config_attributes:

config_attributes
-----------------

    .. method:: config_attributes(self)
    
    Return a ``dict``, where:
    
    * ``sqlschema`` includes a string with the name of the database schema.
    
      .. note:: we suggest you to call with the same name both the schema and the
                package. For more information, check the
                :ref:`introduction to a package <genro_packages_introduction>`.
                
.. * ``reserved`` (boolean); if ``True``... add??? Found it as reserved='y' in the 
    
    * ``comment`` includes a comment string.
    * ``name_short`` includes a string of the :ref:`genro_name_short` of the schema.
    * ``name_long`` includes a string of the :ref:`genro_name_long` of the schema.
    * ``name_plural`` includes a string of the :ref:`genro_name_plural` of the schema.
    
    **Example:**
    
    ::
    
        def config_attributes(self):
            return dict(sqlschema='agenda',
                        comment='an useful comment',
                        name_short='agenda',
                        name_long='agenda',
                        name_full='agenda')
                        
.. _methods_config_db:

config_db
---------
    
    .. deprecated:: 0.7
    
    .. warning:: this method is not used anymore in the ``main.py``, but it is used only as the
                 main method of a database :ref:`genro_table`.
                 
.. _methods_custom_type:

custom_type
-----------

    .. method:: custom_type_CUSTOM-DTYPE(self)
    
    With this method you can create your own :ref:`genro_datatype`.
    
    In the method definition, ``CUSTOM-DTYPE`` is the name you choose for your custom type.
    
    This method returns a ``dict`` through which you can modify the features of your custom
    type. In particular:
    
    * ``dtype`` specify the datatype format (``C`` for char, ``DH`` for datetime... [#]_)
    * ``size`` specify the lenght of the custom datatype.
    * ``default`` specify a default value for the custom datatype.
    
    **Example:**
    
    ::
    
        def custom_type_money(self):
            return dict(dtype='N', size='12,2', default=0)
            
    (the ``dtype='N'`` means that the type is numerical, the ``size='12,2'`` means a field
    of 12 characters with two decimals, the ``default=0`` means that if user don't specify
    the custom_type value, then it is ``0``).
            
    This allows to create in a :ref:`genro_table` a :ref:`table_column` like this one::
    
        tbl.column('partners_income',dtype='money',name_long='Partners Income')
        
    where the ``dtype`` of the column is the custom one we created (``money``).
        
.. _methods_loginUrl:

loginUrl
--------

    Define the location of your login authorization page.
    
    ::
    
            def loginUrl(self):
                return 'packageName/loginName'
                
    where:
    
    * ``packageName`` is the name of the :ref:`package <genro_packages_index>` that contains
      the login authorization page.
    * ``loginName`` is the name of the :ref:`webpages_webpages` in which you define the login
      authorization. For more information on how to build a login page, please check the
      :ref:`genro_login` documentation page.
      
.. add??? Understand if the following methods are old or new...
.. 
.. def newUserUrl(self):
..     return 'adm/new_user'
.. 
.. def modifyUserUrl(self):
..     return 'adm/modify_user'
.. 
.. def onApplicationInited(self):
..     pass
..     
.. def onSiteInited(self):
..     db=self.application.db
..     db.table('sys.locked_record').clearExistingLocks()
..     db.closeConnection()
..
.. def mailLog(self, subject):
..     (...)

.. _main_table_class:

Table class
===========
    
    .. class:: Table(GnrDboTable)
    
    The ``Table`` class is used for ... add???
    
    We list now all the methods of the ``Table`` class:
    
    add???
    
**Footnotes**:

.. [#] Check the complete list of dtypes format in the :ref:`datatype_format` section.
    