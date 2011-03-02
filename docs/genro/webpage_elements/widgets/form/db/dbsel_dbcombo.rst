.. _genro_dbselect_dbcombobox:
	
==========================================
dbSelect and dbCombobox: common attributes
==========================================

    * :ref:`db_genro_attributes`
    * :ref:`db_examples`: :ref:`db_selected`, :ref:`db_condition`, :ref:`db_columns` and :ref:`db_auxColumns`

.. _db_genro_attributes:

Common attributes
=================

    Here we show the attributes that belong both to :ref:`genro_dbselect` than to :ref:`genro_dbcombobox`:
    
    +--------------------+---------------------------------------------------+--------------------------+
    |   Attribute        |          Description                              |   Default                |
    +====================+===================================================+==========================+
    | *dbtable*          | MANDATORY - Select the database                   |  ``None``                |
    |                    | :ref:`genro_database_table` for database widget   |                          |
    |                    | query. For further details, check the             |                          |
    |                    | :ref:`genro_dbtable` explanation page             |                          |
    +--------------------+---------------------------------------------------+--------------------------+
    | *alternatePkey*    | Alternate primary key: allow to save user choice  |  ``None``                |
    |                    | through a different parameter respect to the      |                          |
    |                    | default ID. You can set any other field's         |                          |
    |                    | parameter as alternatePkey                        |                          |
    +--------------------+---------------------------------------------------+--------------------------+
    | *auxColumns*       | Show in a pop-up menu below the input textbox     |  ``None``                |
    |                    | query parameters (*columns* is MANDATORY).        |                          |
    |                    | Check :ref:`db_auxColumns` explanation for        |                          |
    |                    | further details                                   |                          |
    +--------------------+---------------------------------------------------+--------------------------+
    | *columns*          | Check :ref:`db_columns` explanation for           |  ``None``                |
    |                    | further details                                   |                          |
    +--------------------+---------------------------------------------------+--------------------------+
    | *condition*        | Start a SQL query. Check :ref:`db_condition`      |  ``None``                |
    |                    | example for further details                       |                          |
    +--------------------+---------------------------------------------------+--------------------------+
    | *disabled*         | If True, user can't act on the widget.            |  ``False``               |
    |                    | For more details, see :ref:`genro_disabled`       |                          |
    +--------------------+---------------------------------------------------+--------------------------+
    | *hidden*           | Hide the widget. See :ref:`genro_hidden`          |  ``False``               |
    +--------------------+---------------------------------------------------+--------------------------+
    | *label*            | You can't use the *label* attribute; if you       |  ``None``                |
    |                    | want to give a label to your widget, check the    |                          |
    |                    | :ref:`lbl_formbuilder` example                    |                          |
    +--------------------+---------------------------------------------------+--------------------------+
    | *limit*            | Set the number of visible choices on the pop-up   |  ``10``                  |
    |                    | menu below the input textbox during user typing   |                          |
    +--------------------+---------------------------------------------------+--------------------------+
    | *rowcaption*       | Allow user to view records through                |  ``None``                |
    |                    | :ref:`genro_name_long` value.                     |                          |
    |                    | Without *rowcaption*, user will see value ID.     |                          |
    |                    | Check for more information the                    |                          |
    |                    | :ref:`genro_database_rowcaption` page             |                          |
    +--------------------+---------------------------------------------------+--------------------------+
    | *selected*         | You can add different parameters with the sintax: |  ``None``                |
    |                    | ``selected_nameOfATableColumn='datapathFolder'``. |                          |
    |                    | See :ref:`db_selected` example for further details|                          |
    +--------------------+---------------------------------------------------+--------------------------+
    | *value*            | Set a path for widget's values.                   |  ``None``                |
    |                    | For more details, see :ref:`genro_datapath`       |                          |
    +--------------------+---------------------------------------------------+--------------------------+
    | *visible*          | if False, hide the widget (but keep a place in the|  ``True``                |
    |                    | :ref:`genro_datastore` for it). For more          |                          |
    |                    | information, check the :ref:`genro_visible`       |                          |
    |                    | documentation page                                |                          |
    +--------------------+---------------------------------------------------+--------------------------+
    
.. _db_examples:

Examples
========

.. _db_selected:

Selected
========

    With the *selected* attribute you can draw multiple attributes to the :ref:`genro_datastore` through a single *dbSelect* or ``dbCombobox``; the sintax is ``selected_nameOfATableColumn='datapathFolder'``.

    **Example:**

    let's consider a simple Genro Project [#]_ including a database :ref:`genro_database_table` and a :ref:`genro_GnrCustomWebPage`. 

    The table includes a list of actors::

        # encoding: utf-8

        class Table(object):
            def config_db(self,pkg):
                tbl = pkg.table('person',pkey='id',rowcaption='$name')
                tbl.column('id',size='22',group='_',readOnly=True,name_long='Id')
                tbl.column('name',name_short='N.',name_long='Name')
                tbl.column('year','L',name_short='Yr',name_long='Birth Year')
                tbl.column('nationality',name_short='Ntl',name_long='Nationality')
                tbl.column('number','L',name_long='!!Number')

    here we show the webpage::

        class GnrCustomWebPage(object):
            def main(self,root,**kwargs):
                fb = root.formbuilder(cols=2,border_spacing='10px',datapath='myform')
                fb.dbSelect(dbtable='showcase.person',value='^.person_id',lbl='Star',
                            selected_name='.name',selected_year='.year')

    This dbSelect allows user to choose from the ``table`` called "person" an actor; after user choice has been done, the dbSelect will do these operations:

    * a save of the auctor's ID into the :ref:`genro_datastore` at the path: ``/myform/person_id``;
    * through the syntax ``selected_name='.name'``, dbSelect will do a save of the value of the actor's column named "name" into the path: ``/myform/name``;
    * through the syntax ``selected_year='.year'``, dbSelect will do a save of the value of the actor's column named "year" into the path: ``/myform/year``;
    
    So, for example, if user will choose "Cate Blanchett" from the actors' list, Genro will save the following values in the following folders::
        
        /myform/person_id/EuSy8OPJP_Kax4yGokSauw
        /myform/name/"Cate Blanchett"
        /myform/year/1969

.. _db_condition:

Condition
=========

    With the ``condition`` attribute you can write a SQL query.
    
    **syntax**::
    
        condition='$tableColumnName'=:'something'
        
    where 'something' is the SQL condition, expressed through::
    
        condition_something='=PathOfValue'
        
    **Example:** let's start from the previous example (:ref:`db_selected`) where we had a list of actors included into a ``table`` called "person". Let's introduce a ``table`` called "movie" that contains a lot of title films on which the actors have participated::

        # encoding: utf-8

        class Table(object):
            def config_db(self,pkg):
                tbl = pkg.table('movie',pkey='id')
                tbl.column('id',size='22',group='_',readOnly=True,name_long='Id')
                tbl.column('title',name_short='Ttl.',name_long='Title',
                            validate_case='capitalize',validate_len='3,40')
                tbl.column('genre',name_short='Gnr',name_long='Genre',
                            validate_case='upper',validate_len='3,10',indexed=True)
                tbl.column('year', 'L', name_short='Yr',name_long='Year',indexed=True)
                tbl.column('nationality', name_short='Ntl', name_long='Nationality')
                tbl.column('description', name_short='Dsc', name_long='Movie description')
                tbl.column('number','L',name_long='!!Number')

    The two tables ("movie" and "person") will be linked through a :ref:`table_relation` table called "cast"::

        # encoding: utf-8

        class Table(object):
            def config_db(self,pkg):
                tbl = pkg.table('cast',pkey='id',rowcaption='@movie_id.title',
                                 name_long='!!Cast',name_plural='!!Casts')
                tbl.column('id',size='22',group='_',readOnly=True,name_long='Id')
                tbl.column('movie_id',size='22', name_short='Mid', 
                            name_long='Movie id').relation('movie.id',mode='foreignkey')
                tbl.column('person_id',size='22',name_short='Prs', 
                            name_long='Person id').relation('person.id',mode='foreignkey')
                tbl.column('role', name_short='Rl.',name_long='Role')
                tbl.column('prizes', name_short='Priz.',name_long='Prizes', size='40')
                tbl.column('number','L',name_long='!!Number')

    Finally, let's introduce a :ref:`genro_GnrCustomWebPage`::

        class GnrCustomWebPage(object):
            def main(self,root,**kwargs):
                fb = root.formbuilder(cols=2,border_spacing='10px',datapath='myform')
                fb.dbSelect(dbtable='showcase.person',value='^.person_id',lbl='Star')
                fb.dbSelect(dbtable='showcase.movie',value='^.movie_id',lbl='Movie',
                            condition='$person_id=:pid',condition_pid='=.person_id',
                            alternatePkey='movie_id')
                            
    The first dbSelect allows the user to choose an actor from the database. The second dbSelect allows the user to choose from a movie made exclusively by the chosen actor.

.. _db_columns:

Columns
=======

    When a user begins to type something into the ``dbSelect`` (or ``dbCombobox``) field, he will see visualized the database columns specified into the *rowcaption* field.

    The usual procedure of a ``dbSelect`` query is *to search* through the records owned by the *rowcaption* attribute and *to save* the record chosen by the user through record's ID into the :ref:`genro_datastore`.

    If you define ``columns``, the ``dbSelect`` will continue to visualize only the records owned by the *rowcaption* attribute, but ``dbSelect`` will search ONLY through the record columns defined in the ``columns`` attribute.

.. _db_auxColumns:

auxColumns
==========

    The ``auxColumns`` attribute allow to visualize in a menu below the dbSelect (or dbCombobox) some additional fields.

    **Example**::

        class GnrCustomWebPage(object):
            def main(self,root,**kwargs):
                root.dbCombobox(dbtable='showcase.person',value='^.person_id',
                                lbl='Star', auxColumns='$nationality')

**Footnotes:**

.. [#] For more information on a creation of a project, check the :ref:`genro_simple_introduction` page.