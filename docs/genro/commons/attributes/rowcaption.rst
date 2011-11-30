.. _rowcaption:

==========
rowcaption
==========
    
    *Last page update*: |today|
    
    .. note:: **validity** - the *rowcaption* attribute is supported by:
              
              * :ref:`dbcombobox`
              * :ref:`dbselect`
              * :ref:`field`
              
    * :ref:`rowcaption_def`
    * :ref:`rowcaption_syntax`
    * :ref:`rowcaption_examples`:
    
        * :ref:`rowcaption_examples_table`
        * :ref:`rowcaption_examples_webpage`
        
.. _rowcaption_def:

description
===========

    The *rowcaption* attribute is the textual representation of a record in a user query
    
    .. warning:: if you don't specify the *rowcaption* attribute, user will see the
                 :ref:`nodeid` of the record choosen, so remember to specify it!
                 
    It can be defined:
    
    #. directly into a :ref:`database table <table>` (:ref:`rowcaption_examples_table`)
    #. in a query field (a :ref:`field`, a :ref:`dbselect` or a :ref:`dbcombobox`) placed
       into a :ref:`webpage` (:ref:`rowcaption_examples_webpage`)
       
    If you define it in a table, then its value becomes the default of all the :ref:`widgets`
    that refers themselves to that table. You can obviously redefine the "rowcaption" inside
    a widget: in that case the value redefined prevails on the value defined in the table
    
.. _rowcaption_syntax:

syntax
======

    The syntax is: ``$`` followed by the name of a :ref:`column`::
    
        rowcaption='$COLUMNNAME'
        
    Where COLUMNNAME is the name of the column you want that will be visualized
    
    You can add more than one column in the rowcaption, like::
    
        rowcaption='$name,$nationality'
        
    The graphical result is the list of attributes separated by a "-", like::
    
        Alfred Hitchcock - UK
        
    You can customize the visual representation. For example::
    
        rowcaption='$name,$nationality:%s: %s' # where the %s: %s are placeholders providing an
                                               # alternate way to format the rowcaption with fields
                                               # and additional characters
                                               
    Obviously, you can also use a :ref:`table_relation_column` (through the :ref:`"@" syntax <at_char>`)
    
.. _rowcaption_examples:
    
examples
========
    
.. _rowcaption_examples_table:

table example
-------------

    Let's see an example with the *rowcaption* attribute set on a :ref:`database table <table>`.
    The table will be::
    
        class Table(object):
            def config_db(self, pkg):
                tbl = pkg.table('person',pkey='id',rowcaption='$name',
                                 name_long='!!people',name_plural='!!People')
                                 
    The webpage will be::
    
        class GnrCustomWebPage(object):
            def main(self,root,**kwargs):
                fb=pane.formbuilder(datapath='test1')
                fb.dbSelect(dbtable='showcase.person',
                            value='^.person_id',lbl='People')
                fb.dbSelect(dbtable='showcase.person',rowcaption='$surname',
                            value='^.person_id',lbl='People')
                            
    When user types in the first :ref:`dbselect`, he will see the names of the people, because
    the rowcaption attribute in the table is set to the column name called "name".
    
    When user types in the second dbSelect he will see the surname of the people, because
    the *rowcaption* in the dbSelect override the value set through the *rowcaption* of the table
    
    .. _rowcaption_examples_webpage:

webpage example
---------------

    Let's see an example with the *rowcaption* attribute set on a :ref:`webpage`.
    The table would be the same table of the previous example, but there won't be anymore
    the *rowcaption*::

        class Table(object):
            def config_db(self, pkg):
                tbl = pkg.table('person',pkey='id',
                                 name_long='!!people',name_plural='!!People')
                                 
    In the webpage, like::
    
        class GnrCustomWebPage(object):
            def main(self,root,**kwargs):
                fb=pane.formbuilder(datapath='test1')
                fb.dbSelect(dbtable='showcase.person',rowcaption='$name',
                            value='^.person_id',lbl='People')
                            
    When user types in the :ref:`dbselect`, he will see the names of the people, because
    the rowcaption attribute in the webpage is set to the column name called "name"
    