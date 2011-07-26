.. _packages_main:

===========
``main.py``
===========
    
    *Last page update*: |today|
    
    .. image:: ../../_images/projects/packages/main.png
    
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
    
    The ``main.py`` has to begin with a line code that specify the location to the python
    executable in your machine::
    
        #!/usr/bin/env python
    
    Then follows the encoding definition line::
    
        # -*- coding: utf-8 -*-
        
    (here we set the encoding to 'utf-8').
    
    The next line is written for the packages importation::
    
        from gnr.app.gnrdbo import GnrDboTable, GnrDboPackage, Table_counter, Table_userobject
    
    .. warning:: the importation of these four packages is MANDATORY for a correct use of
                 the ``main.py`` file.
                 
    In the ``main.py`` file you have many classes through which you can customize it:
    
    * the :ref:`main_package_class`
    * the :ref:`main_table_class`
    
.. * the add??? other classes?
    
.. _main_package_class:

Package class
=============
    
    *class* **Package** (*GnrDboPackage*)
    
    The ``Package`` class is used for ... add???
    
    We list now all the methods of the ``Package`` class:

.. _methods_config_attributes:

config_attributes
-----------------

    **config_attributes** (*self*)
    
    Return a ``dict``, where:
    
    * ``sqlschema`` includes a string with the name of the database schema.
    
      .. note:: we suggest you to call with the same name both the schema and the
                package. For more information, check the :ref:`about_schema`
                documentation section.
                
    * ``comment`` includes a comment string.
    * ``name_short`` includes a string of the :ref:`name_short` of the schema.
    * ``name_long`` includes a string of the :ref:`name_long` of the schema.
    * ``name_plural`` includes a string of the :ref:`name_plural` of the schema.
    
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
    
    .. warning:: this method is not used anymore in the ``main.py``, but it is used only as the
                 main method of a database :ref:`table`.
                 
.. _methods_custom_type:

custom_type
-----------

    **custom_type_CUSTOMNAME** (*self*)
    
    With this method you can create your own :ref:`datatype`.
    
    ``CUSTOMNAME`` is the name you choose for your custom type.
    
    This method returns a ``dict`` through which you can modify the features of
    your custom type. In particular:
    
    * ``default`` specify a default value for the custom datatype
    * ``dtype`` specify the datatype format (``C`` for char, ``DH`` for datetime... [#]_)
    * ``format`` Specify the punctuation. For example you can specify the character that
      specifies the separation between integers and the decimals.
      
      Example::
        
        format='#.###,00'
        
    * ``size`` specify the lenght of the custom datatype
    
        **Example:**
        
        ::
        
            def custom_type_money(self):
                return dict(dtype='N', size='12,2', default=0)
                
        (the ``dtype='N'`` means that the type is numerical, the ``size='12,2'`` means a field
        of 12 characters with two decimals [#]_, the ``default=0`` means that if user don't specify
        the custom_type value, then it is ``0``).
                
        This allows to create in a :ref:`table` a :ref:`table_column` like this one::
        
            tbl.column('partners_income',dtype='money',name_long='Partners Income')
            
        where the ``dtype`` of the column is the custom one we created (``money``).
        
.. _methods_loginUrl:

loginUrl
--------

    **loginUrl** (*self*)
    
    Define the location of your login authorization page.
    
    ::
    
            def loginUrl(self):
                return 'packageName/loginName'
                
    where:
    
    * ``packageName`` is the name of the :ref:`package <packages_index>` that contains
      the login authorization page.
    * ``loginName`` is the name of the :ref:`webpages_webpages` (without its ``.py`` extensions)
      in which you define the login authorization.
      
        **Example:** if you have a package called ``staff`` and your login webpage is called
        ``my_great_login.py``, then your ``loginUrl`` method should be::
        
            def loginUrl(self):
                return 'staff/my_great_login'
                
    .. note:: We suggest you to use ``login.py`` as default name for the login page; if you do so,
              your ``loginUrl`` should be::
              
                def loginUrl(self):
                    return 'packageName/login'
                    
              where ``packageName`` is the name of your package.
    
    For more information on how to build a login page, please check the :ref:`login_auth`
    documentation page.
    
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
    
    *class* **Table** (*GnrDboTable*)
    
    The ``Table`` class is used for ... add???
    
    We list now all the methods of the ``Table`` class:
    
    add???
    
**Footnotes**:

.. [#] Check the complete list of dtypes format in the :ref:`datatype_format` section.
.. [#] If you have ``size='12,2'`` and write two decimals, you can use only 10 integers. If you have one decimal you can write 11 integers.
    