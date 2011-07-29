.. _paths:

=====
paths
=====

    *Last page update*: |today|
    
    * :ref:`paths_intro`
    * :ref:`rel_creation`
    * :ref:`relation_path`
    * :ref:`inv_rel_path`
    * :ref:`path_examples`: :ref:`path_example_one`
    
.. _paths_intro:
    
introduction
============

    You can create a relation between two or more database :ref:`tables <table>`. To create these
    relations, you have to follow the steps of the :ref:`next <rel_creation>` section.
    
    When you create a relation, you can walk this connection in a direction or in the opposite one:
    
    * if you walk the direction in the normal direction, we talk about :ref:`relation_path`
    * if you walk in the inverse direction, we talk about :ref:`inv_rel_path`
    
    So, the path is the same but we make a distinction between the direct direction and the
    inverse direction because they support a different syntax.
    
.. _rel_creation:

creation of a relation
======================

    To create a relation, you have to:
    
    1. create a :ref:`table`:
    
        1a. create in your :ref:`table` the following introductory lines::
            
            #!/usr/bin/env python
            # encoding: utf-8
            
            class Table(object):
                def config_db(self, pkg):
                 
        1b. in the ``config_db`` method you have to attach the table to the pkg object
        
            **Example**::
            
                tbl = pkg.table('exam',pkey='id',name_long='Exam',name_plural='Exams')
                
    2. then you have to create a :ref:`table_relation_column` by making a :ref:`table_column` and
       attaching to it the :ref:`table_relation`
       
        **Example**::
        
             tbl.column('stud_id',size='22',name_long='Student ID').relation('school.student.id',mode='foreignkey')
             
        ``column`` parameters:
        
        * ``stud_id`` is a mandatory name for the relation column, that is a column through which you have
          made the relation
        * ``size`` is the column lenght; we put ``22`` because the ID lenght is 22
        * ``name_long`` is used for the visualization of the column (more information :ref:`here <name_long>`)
        
        ``relation`` parameters:
        
        * ``school.student.id`` is a string composed by the name of the package that includes the table
          to relate (``school``), the name of the table to relate (``student``) and its :ref:`pkey` (``id``)
        * ``mode='foreignkey'`` is a string that transform the relation in a SQL relation
        
       .. note:: You can get more information on the points 1a and 1b in the :ref:`table` documentation page.
                 You can get more information on the point 2 in the example :ref:`below <path_example_one>`
                 and in the definition of the :ref:`table_relation`.
    
.. _relation_path:

relation path
=============

    **Definition**:
    
        A **relation path** is a relation established between two tables that follows
        the direction from the table in which you have created the relation to the table related.
        
            *In the following image, the table A is the table related to the table B.*
            
            *So the direct link, that is the arrow in the direction from A to B, is the relation path*
        
        .. figure:: ../_images/sql/rel_path.png
        
        The walk in the inverse direction (that is, from the table related to the table in which
        you have created the relation) is called the :ref:`inv_rel_path`.
        
    **Syntax**:
    
        When you have a relation (you can create it through the instructions of the :ref:`rel_creation`
        section), you can create a relation path. You need a relation path to get your data from a table
        to a related table.
        
        To create a relation path in a :ref:`webpages_webpages` (or in a :ref:`th_resource_page`)
        to a specified COLUMN you have to use this syntax::
        
            @RelationColumnName.COLUMN
            
        where:
        
        * ``@`` is the char used in Genro to begin a *path in relation* [#]_
        * ``RelationColumnName`` is the :ref:`table_relation_column` name
        * ``COLUMN`` is the name of the column in the related table that you need to link your object
        
.. _inv_rel_path:

inverse relation path
=====================

    **Definition**:
    
    An **inverse relation path** is a relation established between two tables that follows
    the direction from the table related to the table in which you have created the relation.
    
        *In the following image, the table A is related to the table B.*
        
        *So the direct link (the straight arrow) is the relation path and the inverse link*
        *(the curved line) is the inverse relation path*
    
    .. image:: ../_images/sql/inv_rel_path.png
    
    **Syntax**:
    
    To create an *inverse relation path*, you have to:
    
    #. create a :ref:`table_relation_column`
    #. add the :ref:`relation_name` in the relation column
    
.. _relation_name:

relation_name
-------------

    An attribute of the :ref:`table_relation`. It allows to define the :ref:`inv_rel_path`.
    
    By default, the relation name follow this syntax::
    
        @packageName_tableName_relatedName
        
    where:
    
    * ``@`` is the char used in Genro to begin a *path in relation*
    * ``packageName`` is the name of the :ref:`package <packages_index>`
    * ``tableName`` is the name of the :ref:`table`
    * ``relatedName`` is the name of the related_column, that is the first parameter of the
      :ref:`table_relation`
      
    You can clearly overwrite the default name of the relation_name. In that case, the
    ``relation_name`` is not anymore ``@packageName_tableName_relatedName``, but ``@NameYouGive``
    
        **Example**:
        
        If you have the following :ref:`table_relation_column`::
        
          tbl.column('stud_id',size='22',name_long='Student ID').relation('school.student.id',mode='foreignkey')
          
        where the packageName is "school", the tableName is "student" and the relatedName is "stud_id",
        the automatic ``relation_name`` is::
        
          @school_student_stud_id
          
        **Example**:
        
        If you add a ``relation_name`` to the relation column::
        
          tbl.column('stud_id',size='22',name_long='Student ID').relation('school.student.id',mode='foreignkey',
                                                                           relation_name='students')
                                                                           
        The relation_name is not anymore ``school_student_stud_id``, but::
        
            @students
            
.. _path_examples:

examples
========

.. _path_example_one:

relation path, inverse relation path
------------------------------------

    Let's describe a small set of :ref:`tables <table>` to explain how the concepts of
    :ref:`relation_path` and :ref:`inv_rel_path` work in a Genro :ref:`project`.
    
    We want to describe the inscription to some college exams, so we need three tables: one for the
    *students*, one for the *exams* and one for the *exam registrations*.
    
    Let's start writing the code of the easier two tables: the student table and the exam table.
    
    * **student table**::
        
        1   #!/usr/bin/env python
        2   # encoding: utf-8
        3   
        4   class Table(object):
        5       def config_db(self, pkg):
        6           tbl = pkg.table('student',pkey='id',name_long='Student',name_plural='Students')
        7           self.sysFields(tbl)
        8           tbl.column('name',name_long='Name')
                
    where:
    
    * line 1 - defined the environment location of the Python application
    * line 2 - defined the encoding
    * lines 4 and 5 - called the ``Table`` class and the ``config_db`` method that
      will handle all the stuff about our table
    * line 6 - created the table, specifying its name (``student``)
      and its primary key (the :ref:`pkey`)
    * line 7 - introduced the :ref:`sysfields` method that allows to create the id column
      (it does other things, too, but they are not important to be known for this example)
    * line 8 - created the ``Name`` :ref:`table_column`, including the students' name
    
    You can find more information on the creation of a table :ref:`clicking here <table>`.
    
    Now let's write down the code for the *exam* table:
    
    * **exam table**::
        
        1   #!/usr/bin/env python
        2   # encoding: utf-8
        3   
        4   class Table(object):
        5       def config_db(self, pkg):
        6           tbl = pkg.table('exam',pkey='id',name_long='Exam',name_plural='Exams')
        7           self.sysFields(tbl)
        8           tbl.column('name',name_long='Name')
        9           tbl.column('professor',name_long='Professor')
                
    There anything different form the previous table.
    
    Through the last table, called *exam registrations*, we link the three tables one each other.
    
    * **exam registration table**::
    
        1   #!/usr/bin/env python
        2   # encoding: utf-8
        3   
        4   class Table(object):
        5       def config_db(self, pkg):
        6           tbl = pkg.table('exam',pkey='id',name_long='Exam',name_plural='Exams')
        7           self.sysFields(tbl)
        8           tbl.column('date','D',name_long='Date')
        9           tbl.column('stud_id',size='22',name_long='Student ID').relation('student.id',mode='foreignkey',
        10                                                                           relation_name='stud_registrations')
        11          tbl.column('exam_id',size='22',name_long='Exam ID').relation('exam.id',mode='foreignkey',
        12                                                                           relation_name='ex_registrations')
                                                                              
    where:
    
    * lines 1 to 8 - these lines are similar to the code of the previous tables
    * line 9 - we create the :ref:`relation_path` between the *student* table and the *exam registration*
    * line 10 - the :ref:`relation_name` is an attribute that create the :ref:`inv_rel_path` between
      the *student* table and the *exam registration*
    * line 11 - we create the :ref:`relation_path` between the *exam* table and the *exam registration*
    * line 12 - the :ref:`relation_name` is an attribute that create the :ref:`inv_rel_path` between
      the *exam* table and the *exam registration*
      
    Let's see now how can you link from a table to another:
    
    add??? continue from here!
    
    * If you are in the *exam registration* table and you have to check the columns of the
      *exam* table, you have to follow a direct :ref:`relation_path`:
      
        * for the *name* column::
        
            @exam_id.name
            
        * for the *professor* column::
            
            @exam_id.professor
            
    * If you are in the *exam registration* table and you have to check the columns of the
      *student* table, you have to follow a direct :ref:`relation_path`:
      
        * for the *name* column::
        
            @stud_id.name
            
    * If you need to check the columns of the *exam* table from the *student* table you have
      to make the following path::
      
        @stud_registrations.exam_id.COLUMN
        
      adding in place of COLUMN the column of the *exam* table you want.
      
      So if you want to check the "name" column the path will be::
      
        @stud_registrations.exam_id.name
        
      and if you want to check the "professor" column the path will be::
        
        @stud_registrations.exam_id.professor
        
    add??? ripeto da linea 139 in giù partendo da *exam* e andando in *student*...
      
    add??? image!
    
**Footnotes**:

.. [#] The ``@`` is also used as the first character of an inverse relation path.