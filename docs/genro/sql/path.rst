.. _rel_paths:

==============
relation paths
==============

    *Last page update*: |today|
    
    * :ref:`paths_intro`
    * :ref:`relation`
    * :ref:`relation_path`
    * :ref:`inv_rel_path`
    * :ref:`composed_path`
    * :ref:`path_examples`: :ref:`path_example_one`
    
.. _paths_intro:
    
introduction
============

    You can create a relation between two or more database :ref:`tables <table>`.
    We explain the steps to create these relations in the :ref:`next <relation>` section.
    
    When you create a relation, you can walk this connection in a direction or in the opposite one:
    
    * if you walk the direction in the normal direction, we talk about :ref:`relation_path`
    * if you walk in the inverse direction, we talk about :ref:`inv_rel_path`
    
    .. image:: ../_images/sql/path.png
    
    So, the relation is ONE but we make a distinction between the direct direction and the
    inverse direction because they support a different syntax.
    
    **Usage**:
    
    Once you have created your relation path, you can use it to use data of a table in another
    related table.
    
    There are many objects through which you can use relation paths (and inverse relation paths):
    
    * for the complete list, check the :ref:`at_usage` section
    * for examples on their usage, check the :ref:`path_examples` section
    
.. _relation:

relation
========

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
        
       .. note:: You can get more information on the points 1a and 1b in the :ref:`table` page.
                 You can get more information on the point 2 in the :ref:`path_examples` below
                 and in the definition of the :ref:`table_relation`.
    
.. _relation_path:

relation path
=============

    **Definition**:
    
        A **relation path** is a relation established between two tables that follows
        the direction from the table in which you have created the relation to the table related.
        
            *In the following image, the table A is linked through the relation method to the table B.*
            
            *So the direct link, that is the arrow in the direction from A to B, is the relation path*
        
        .. figure:: ../_images/sql/rel_path.png
        
        The walk in the inverse direction (that is, from Table A to table B) is called the
        :ref:`inv_rel_path`.
        
    **Syntax**:
    
        Once you have a relation (you can create it through the instructions of the :ref:`relation`
        section), you can create a relation path. You need a relation path to get your data from a table
        to a related table.
        
        To create a relation path to get some data from a database table you have to use this syntax::
        
            @RelationColumnName.COLUMN
            
        where:
        
        * ``@`` is the char used in Genro to begin a *path in relation* (for more information check the
          :ref:`at_char` page)
        * ``RelationColumnName`` is the :ref:`table_relation_column` name
        * ``COLUMN`` is the name of the column you want to get from the related table
        
        For more information, check the :ref:`path_examples` below.
        
.. _inv_rel_path:

inverse relation path
=====================

    **Definition**:
    
        An **inverse relation path** is a relation established between two tables that follows
        the direction from the table related to the table in which you have created the relation.
        
            *In the following image, the table A is linked through the relation method to the table B*
            
            *The direct link (the straight arrow) is the "relation path"*
            
            *The inverse link (the curved line) is the "inverse relation path"*
        
        .. image:: ../_images/sql/inv_rel_path.png
        
        You don't need to create the *inverse relation path*, you just created it when you created the
        :ref:`relation_path`.
    
    **Syntax**:
    
        By default, the *inverse relation path* is::
        
            @packageName_tableName_relatedName
            
        where:
        
        * ``@`` is the char used in Genro to begin a *path in relation* (for more information check the
          :ref:`at_char` page)
        * ``packageName`` is the name of the :ref:`package <packages_index>`
        * ``tableName`` is the name of the :ref:`table`
        * ``relatedName`` is the name of the related_column, that is the first parameter of the
          :ref:`table_relation`
          
            **Example**:
            
            If you have the following :ref:`table_relation_column`::
            
              tbl.column('stud_id',size='22',name_long='Student ID').relation('school.student.id',mode='foreignkey')
              
            where the packageName is "school", the tableName is "student" and the relatedName is "stud_id",
            the automatic ``relation_name`` is::
            
              @school_student_stud_id
              
        You can change the default string of the *inverse relation path* through the :ref:`relation_name`
        
            .. _relation_name:

relation_name
-------------

    An attribute of the :ref:`table_relation`. It allows to estabilish an alternative string
    for the :ref:`inv_rel_path`.
    
    If you use the ``relation_name``, the *inverse relation path* string is not anymore
    ``@packageName_tableName_relatedName``, but it will be::
    
        @NameYouGave
        
    where:
    
    * ``@`` is the char used in Genro to begin a *path in relation* (for more information check the
      :ref:`at_char` page)
    * ``NameYouGave`` is the string you choose for the ``relation_name``
        
        **Example**:
        
        If you add a ``relation_name`` to the relation column::
        
          tbl.column('stud_id',size='22',name_long='Student ID').relation('school.student.id',mode='foreignkey',
                                                                           relation_name='students')
                                                                           
        The relation_name is not anymore ``school_student_stud_id``, but::
        
            @students
            
.. _composed_path:

composed path
=============

    For "composed path" we mean a series of :ref:`relation paths <relation_path>` and :ref:`inverse
    relation paths <inv_rel_path>` one after another. You can find a clear explanation of this in the
    following :ref:`path_examples`.
            
.. _path_examples:

examples
========

.. _path_example_one:

relation path, inverse relation path
------------------------------------

    Let's describe a small set of :ref:`tables <table>` to explain how the concepts of
    :ref:`relation_path` and :ref:`inv_rel_path` work in a Genro :ref:`project`.
    
    We want to describe the inscription to some college exams, so we need three tables: one for the
    *students* (S), one for the *exams* (EX) and one for the *exam registrations* (ER). The ER
    table will be linked both to the other two tables through two :ref:`relation columns 
    <table_relation_column>`:
    
    #. one relation column will be used for the creation of a relation between the ER table
       and the EX table, and the relation carries:
    
        * a *relation path* to get data from ER to EX
        * an *inverse relation path* to get data from EX to ER
        
    #. one relation column will be used for the creation of a relation between the ER table
       and the S table, and the relation carries:
    
        * a *relation path* to get data from ER to S
        * an *inverse relation path* to get data from S to ER
    
    .. image:: ../_images/sql/path_example.png
    
    Let's start writing the code of the easier two tables: the S table and the EX table.
    
    * **student table (S)**::
        
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
    
    * **exam table (EX)**::
        
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
    
    Through the last table (ER) we link the three tables one each other.
    
    * **exam registration table (ER)**::
    
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
    * line 9 - we create the :ref:`relation_path` between the ER table and the S table
    * line 10 - the :ref:`relation_name` creates the :ref:`inv_rel_path` between
      the ER table and the S table
    * line 11 - we create the :ref:`relation_path` between the ER table and the EX table
    * line 12 - the :ref:`relation_name` creates the :ref:`inv_rel_path` between the ER
      table and the EX
      
    So we have now this situation:
    
    .. image:: ../_images/sql/path_example_2.png
      
    Let's see how can you get data from a table to another:
    
    * **relation paths**
      
      From the ER table to the EX table, you have to do the following relation paths:
      
      * for the *name* column::
      
        @exam_id.name
        
      * for the *professor* column::
          
        @exam_id.professor
        
      From the ER table to the S table, you have to do the following relation path:
      
      * for the *name* column::
      
        @stud_id.name
        
    * **inverse relation paths**:
      
      From the EX table to the ER table, you have to do the following inverse relation path:
      
      * for the *date* column::
      
        @ex_registrations_date
            
      From the S table to the ER table, you have to do the following inverse relation path:
      
      * for the *date* column::
      
        @stud_registrations_date
        
    * **composed paths (both direct and inverse relation paths)**:
      
      From the EX table to the S table, you have to do the following path:
      
      * for the student "name"::
      
        @ex_registrations.stud_id.name
        
      So, you made an *inverse relation path* (``@ex_registrations``) followed by a relation
      path (``stud_id.name``)
      
      Similarly, from the S table to the EX table, you have to do the following path:
      
      * for the exam "name"::
      
        @stud_registrations.exam_id.name
        
      * for the exam "professor"::

        @stud_registrations.exam_id.professor
        