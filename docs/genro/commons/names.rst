.. _commons_names:

=====
names
=====
    
    *Last page update*: |today|
    
    * :ref:`name_full`
    * :ref:`name_long`
    * :ref:`name_plural`
    * :ref:`name_short`
    * :ref:`names_examples`:
    
        * :ref:`names_examples_table`
        * :ref:`names_examples_cfg_attr`
        * :ref:`names_examples_package`
        
.. _name_full:

name_full
=========

    The "name_full" is a string that can include:
    
    * the full (add??? differences with the "name_long"?) name of a :ref:`database table <table>`
    * the full (add???) name of the :ref:`table columns <table_column>`
    * the full (add???) name of a database schema (check the :ref:`methods_config_attributes` section)
    * the full (add???) name of a :ref:`package <packages_index>`
    
    You can specify multiple languages adding the :ref:`"!!" <exclamation_point>` characters to the
    begin of the string. More information in the :ref:`languages` section
    
    Check the :ref:`names_examples` below
    
.. _name_long:

name_long
=========

    The "name_long" is a string that can include:
    
    * the full (add??? differences with the "name_full"?) name of a :ref:`database table <table>`
    * the full (add???) name of the :ref:`table columns <table_column>`
    * the full (add???) name of a database schema (check the :ref:`methods_config_attributes` section)
    * the full (add???) name of a :ref:`package <packages_index>`
    
    You can specify multiple languages adding the :ref:`"!!" <exclamation_point>` characters to the
    begin of the string. More information in the :ref:`languages` section
    
    Check the :ref:`names_examples` below
    
.. _name_short:

name_short
==========

    The "name_short" is a string that can include:
    
    * the abbreviation name of a :ref:`database table <table>`
    * the abbreviation name of the :ref:`table columns <table_column>`
    * the abbreviation name of a database schema (check the :ref:`methods_config_attributes` section)
    * the abbreviation name of a :ref:`package <packages_index>`
    
    You can specify multiple languages adding the :ref:`"!!" <exclamation_point>` characters to the
    begin of the string. More information in the :ref:`languages` section
    
    Check the :ref:`names_examples` below
    
.. _name_plural:

name_plural
===========

    The "name_plural" is a string that can include:
    
    * the plural name of a :ref:`database table <table>`
    * the plural name of the :ref:`table columns <table_column>`
    * the plural name of a database schema (check the :ref:`methods_config_attributes` section)
    * the plural name of a :ref:`package <packages_index>`
    
    You can specify multiple languages adding the :ref:`"!!" <exclamation_point>` characters to the
    begin of the string. More information in the :ref:`languages` section
    
    Check the :ref:`names_examples` below
    
.. _names_examples:

examples
========

.. _names_examples_table:

names in a table and in the columns
-----------------------------------

    Let's see an example of creation of a table with some columns with the names attribute (if you
    need more information on the creation of a table, please check the :ref:`table` section)::
    
        #!/usr/bin/env python
        # encoding: utf-8
        
        class Table(object):
            def config_db(self, pkg):
                tbl = pkg.table('invoice',pkey='id',name_long='!!Invoice',name_plural='!!Invoices',
                                 rowcaption='$number,$date:%s (%s)')
                tbl.column('id',size='22',group='_',readOnly=True,name_long='!!Id')
                self.sysFields(tbl,id=False)
                tbl.column('number',size='10',name_long='!!Number')
                tbl.column('date','D',name_long='!!Date')
                tbl.column('customer_id',size='22',name_long='!!Customer_ID',validate_notnull=True,
                            validate_notnull_error='!!Customer is mandatory').relation('customer.id',onDelete='raise',
                                                                                        mode='foreignkey',relation_name='invoices')
                tbl.column('net','money',name_long='!!Net')
                tbl.column('vat','N',size='12',name_long='!!Vat')
                tbl.column('total','N',size='15,2',name_long='!!Total')
                tbl.aliasColumn('customer',relation_path='@customer_id.name')
                tbl.aliasColumn('city',relation_path='@customer_id.city')
                
    .. _names_examples_cfg_attr:

names in the config_attributes() method
---------------------------------------

    In the :ref:`packages_main` file of a :ref:`project` you can set the :ref:`methods_config_attributes`
    method through which you define some properties of the database schema::
    
        def config_attributes(self):
            return dict(sqlschema='agenda',
                        comment='an useful comment',
                        name_short='ag.',
                        name_long='agenda',
                        name_full='agenda')
                        
    .. _names_examples_package:

names in the package creation
-----------------------------

    add???
    