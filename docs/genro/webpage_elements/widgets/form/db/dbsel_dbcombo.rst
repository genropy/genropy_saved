.. _genro_dbselect_dbcombobox:
	
==========================================
dbSelect and dbCombobox: common attributes
==========================================

    * :ref:`db_genro_attributes`
    * :ref:`db_examples`: :ref:`db_selected`, :ref:`db_condition`, :ref:`db_columns` and :ref:`db_auxColumns`, :ref:`db_hasdownarrow`

.. _db_genro_attributes:

Common attributes
=================

    Here we show the attributes that belong both to :ref:`genro_dbselect` than to :ref:`genro_dbcombobox`:
    
    ==================== =================================================== ========================== ======================================
       Attribute                   Description                                  Default                       Example                        
    ==================== =================================================== ========================== ======================================
     *dbtable*            MANDATORY - Select the database                      ``None``                 :ref:`genro_dbtable` explanation page
                          :ref:`model_table` for database widget                                                                             
                          query.                                                                                                             
    -------------------- --------------------------------------------------- -------------------------- --------------------------------------
     *alternatePkey*      Alternate primary key: allow to save user choice     ``None``                
                          through a different parameter respect to the                                 
                          default ID. You can set any other field's                                    
                          parameter as alternatePkey                                                   
    -------------------- --------------------------------------------------- -------------------------- --------------------------------------
     *auxColumns*         Show in a pop-up menu below the input textbox        ``None``                 :ref:`db_auxColumns` explanation page
                          query parameters (*columns* becomes MANDATORY).                                                                    
    -------------------- --------------------------------------------------- -------------------------- --------------------------------------
     *columns*            Additional view                                      ``None``                 :ref:`db_columns` example            
    -------------------- --------------------------------------------------- -------------------------- --------------------------------------
     *condition*          Start a SQL query.                                   ``None``                 :ref:`db_condition` example          
    -------------------- --------------------------------------------------- -------------------------- --------------------------------------
     *disabled*           If True, user can't act on the widget.               ``False``                :ref:`genro_disabled` explanation page
    -------------------- --------------------------------------------------- -------------------------- --------------------------------------
     *hasDownArrow*       If True, show an arrow and let the user choose       ``False``                :ref:`db_hasdownarrow` example
                          from all the entries (so, the *limit* attribute                              
                          is overridden.                                         
    -------------------- --------------------------------------------------- -------------------------- --------------------------------------
     *hidden*             Hide the widget.                                     ``False``                :ref:`genro_hidden` explanation page
    -------------------- --------------------------------------------------- -------------------------- --------------------------------------
     *ignoreCase*         If True, allow the user to ignore the case           ``True``                
    -------------------- --------------------------------------------------- -------------------------- --------------------------------------
     *label*              You can't use the *label* attribute; if you          ``None``                 :ref:`lbl_formbuilder` example
                          want to give a label to your widget, check the                               
                          :ref:`lbl_formbuilder` example                                               
    -------------------- --------------------------------------------------- -------------------------- --------------------------------------
     *limit*              Set the number of visible choices on the pop-up      ``10``                  
                          menu below the input textbox during user typing                              
    -------------------- --------------------------------------------------- -------------------------- --------------------------------------
     *rowcaption*         Allow user to view records through                   ``None``                 :ref:`genro_database_rowcaption` page 
                          :ref:`genro_name_long` value.                                                
                          Without *rowcaption*, user will see value ID.                                
    -------------------- --------------------------------------------------- -------------------------- --------------------------------------
     *selected*           You can add different parameters with the sintax:    ``None``                 :ref:`db_selected` example
                          ``selected_nameOfATableColumn='datapathFolder'``.                            
    -------------------- --------------------------------------------------- -------------------------- --------------------------------------
     *value*              Set a path for widget's values.                      ``None``                 :ref:`genro_datapath` explanation page
    -------------------- --------------------------------------------------- -------------------------- --------------------------------------
     *visible*            if False, hide the widget (but keep a place in       ``True``                 :ref:`genro_visible` explanation page
                          the :ref:`genro_datastore` for it).                                           
    ==================== =================================================== ========================== ======================================
    
.. _db_examples:

Examples
========

.. _db_selected:

Selected
========

    With the *selected* attribute you can draw multiple attributes to the :ref:`genro_datastore` through a single *dbSelect* or ``dbCombobox``; the sintax is ``selected_nameOfATableColumn='datapathFolder'``.

    **Example:**

    let's consider a simple Genro Project [#]_ including a database :ref:`model_table` and a :ref:`webpages_GnrCustomWebPage`. 

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

    With the *condition* attribute you can write a SQL query.
    
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
                
    Finally, let's introduce a :ref:`webpages_GnrCustomWebPage`::
    
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

    The usual procedure of a ``dbSelect`` query is to search through the records owned by the *rowcaption* attribute and to save the record chosen by the user through record's ID into the :ref:`genro_datastore`.

    If you define *columns*, the ``dbSelect`` will continue to visualize only the records owned by the *rowcaption* attribute, but ``dbSelect`` will search ONLY through the record columns defined in the *columns* attribute.

.. _db_auxColumns:

auxColumns
==========

    The *auxColumns* attribute allow to visualize in a menu below the dbSelect (or dbCombobox) some additional fields.

    **Example**::

        class GnrCustomWebPage(object):
            def main(self,root,**kwargs):
                root.dbCombobox(dbtable='showcase.person',value='^.person_id',
                                lbl='Star', auxColumns='$nationality')

.. _db_hasdownarrow:

hasDownArrow
============

    If True, the *hasDownArrow* attribute inserts a "down arrow", letting the user the possibility to search between ALL the entries (so the *limit* attribute is overridden)
    
    **Example**::
        
        class GnrCustomWebPage(object):
            def main(self,root,**kwargs):
                fb = root.formbuilder(cols=2, border_spacing='10px', datapath='test1')
                fb.div("""In this test you can see the basic funcionalities of the dbSelect attribute:
                          the "dbtable" attribute allows to search from a database table,""",
                          font_size='.9em', text_align='justify', colspan=2)
                fb.div("""saving the ID of the chosen record.""",
                          font_size='.9em', text_align='justify', colspan=2)
                fb.div('Star (value saved in "test1/person_id")',color='#94697C', colspan=2)
                fb.dbSelect(dbtable='showcase.person', value='^test1.person_id', limit=10, colspan=1)
                fb.div("""Default values for a dbSelect: limit=10 (number of viewed records scrolling the
                          dbSelect), hasDownArrow=False""",
                          font_size='.9em', text_align='justify', colspan=1)
                fb.div('Star (value saved in "test1/person_id_2")',color='#94697C', colspan=2)
                fb.dbSelect(dbtable='showcase.person', value='^test1.person_id_2', hasDownArrow=True)
                fb.div("""The hasDownArrow=True override the limit=10, and let the user see all the entries""",
                          font_size='.9em', text_align='justify', colspan=1)
                          
**Footnotes:**

.. [#] For more information on a creation of a project, check the :ref:`genro_simple_introduction` page.