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
    
        * :ref:`rowcaption_table`
        * :ref:`rowcaption_webpage`
        
.. _rowcaption_def:

description
===========

    The *rowcaption* attribute is the textual representation of a record in a user query
    
    .. warning:: if you don't specify the *rowcaption* attribute, user will see the
                 :ref:`nodeid` of the record choosen, so remember to specify it!
                 
    It can be defined in two places:
    
    * directly into a :ref:`database table <table>`: check the :ref:`rowcaption_table` example
    * in a query field (in a :ref:`field`, in a :ref:`dbselect` or in a :ref:`dbcombobox`)
      placed into a :ref:`webpage`: check the :ref:`rowcaption_webpage` example
      
    If you define it in a table, then its value becomes the default of all the widgets
    that refers themselves to that table. You can obviously redefine the "rowcaption" inside
    a widget: in that case the value redefined prevails on the value defined in the table
    
.. _rowcaption_syntax:

syntax
======

    ::
    
        rowcaption='$COLUMNNAME'
        
    Where COLUMNNAME is the name of the column you want that will be visualized
    
    The syntax is ``$`` followed by the name of a column, like::
    
        rowcaption='$name'
        
    You can add more than one column in the rowcaption, like::
    
        rowcaption='$name,$nationality'
        
    The graphical result is the list of attributes separated by a "-", like::
    
        Alfred Hitchcock - UK
        
    or::
    
        rowcaption='$name,$nationality:%s: %s' # where the %s: %s are placeholders providing an
                                               # alternate way to format the rowcaption with fields
                                               # and addition characters.
                                               
    Obviously, you can also use the "@" syntax (check in :ref:`table` page for further details).
    
.. _rowcaption_examples:
    
examples
========
    
.. _rowcaption_table:

rowcaption - database table
---------------------------

    Let's see an example::

        class Table(object):
            def config_db(self, pkg):
                tbl = pkg.table('person',pkey='id',rowcaption='$name',
                                 name_long='!!people',name_plural='!!People')
                                 
.. _rowcaption_webpage:

rowcaption - query field
------------------------

    Let's see an example on putting the *rowcaption* attribute directly in the webpage::

        class Table(object):
            def config_db(self, pkg):
                tbl = pkg.table('person',pkey='id',
                                 name_long='!!people',name_plural='!!People')

    In this case, we define the table without using the *rowcaption* attribute. We have to put it into the webpage, like::

        class GnrCustomWebPage(object):
            def main(self,root,**kwargs):
                fb=pane.formbuilder(datapath='test1',cols=2)
                fb.field(dbtable='showcase.person',rowcaption='$name',
                         value='^.person_id',lbl='Star')
