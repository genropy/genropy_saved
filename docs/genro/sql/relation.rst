.. _relations:

=========
relations
=========

    *Last page update*: |today|
    
    * :ref:`paths_intro`
    * :ref:`creating_relation`:
    
        * :ref:`relation (or direct relation) <relation>`
        * :ref:`inverse_relation`
        * :ref:`relation_path`
        
    * :ref:`path_examples`: :ref:`path_example_one`
    
.. _paths_intro:
    
introduction
============

    You can create a relation between two or more database :ref:`tables <table>`.
    
    When you create a relation, you can walk it in the direct direction
    or in the inverse direction (and, clearly, the syntax is different):
    
    * if you walk the direction in the direct direction, we talk about :ref:`relation`
    * if you walk in the inverse direction, we talk about :ref:`inverse_relation`
    
    .. image:: ../_images/sql/path.png
    
    **Usage**:
    
    Once you have created your relation, you can use it to use data of a table in another
    related table.
    
    For example, you can use an HTML div, a :ref:`field` or a :ref:`fieldcell` to get data.
    
    * for a complete list of the elements that support the relations, check the
      :ref:`at_usage` section
    * for some examples on the usage of the relations, check the :ref:`path_examples` section
    
.. _creating_relation:

creating a relation
===================

    To create a relation, you have to:
    
    1. create a :ref:`table`:
    
        1a. create in your :ref:`table` the following introductory lines [#]_::
            
            #!/usr/bin/env python
            # encoding: utf-8
            
            class Table(object):
                def config_db(self, pkg):
                 
        1b. in the ``config_db`` method you have to attach the table to the pkg object
        
            **Example**::
            
                tbl = pkg.table('exam',pkey='id',name_long='Exam',name_plural='Exams')
                
    2. then you have to create a :ref:`table_relation_column`; a relation column is a simple
       :ref:`table_column` with the :ref:`table_relation` added:
       
        .. image:: ../_images/sql/relation_column.png
        
        **Example**::
        
             tbl.column('stud_id',size='22',name_long='Student ID').relation('school.student.id',mode='foreignkey')
             
        ``column`` parameters:
        
        * ``stud_id`` is a mandatory name for the relation column, that is a column
          through which you have made the relation
        * ``size`` is the column lenght; we put ``22`` because we use a 22-characters ID
        * ``name_long`` is used for the visualization of the column (more information :ref:`here <name_long>`)
        
        ``relation`` parameters:
        
        * ``school.student.id`` is a string composed by the name of the package that includes the table
          to relate (``school``), the name of the table to relate (``student``) and its :ref:`pkey` (``id``)
        * ``mode='foreignkey'`` is a string that transform the relation in a SQL relation
        
.. _relation:

relation
========

    **Definition**:
    
        A **relation** (or a **direct relation**) is a relation established between two tables that follows
        the direction from the table in which you have created the relation to the table related.
        
            *In the following image, the table A is linked through the relation method to the table B.*
            
            *So the direct link, that is the arrow in the direction from A to B, is the (direct) relation*
        
        .. figure:: ../_images/sql/rel_path.png
        
    **Syntax**:
    
        Once you have a relation (you can create it through the instructions of the :ref:`creating_relation`
        section), you can use it to get your data from a table to a related table.
        
        To use a relation you have to use this syntax::
        
            @RelationColumnName.COLUMN
            
        where:
        
        * ``@`` is the char used in Genro to begin a *relation* (that is, a :ref:`relation`, an
          :ref:`inverse_relation` or a :ref:`relation_path`. For more information check the
          :ref:`at_char` page)
        * ``RelationColumnName`` is the :ref:`table_relation_column` name
        * ``COLUMN`` is the name of the column you want to get from the related table
        
        For more information, check the :ref:`path_examples` below.
        
.. _inverse_relation:

inverse relation
================

    **Definition**:
    
        An **inverse relation** is a relation established between two tables that follows
        the direction from the table related to the table in which you have created the relation.
        
            *In the following image, the table A is linked through the relation method to the table B*
            
            *The direct link (the straight arrow) is the "relation"*
            
            *The inverse link (the curved line) is the "inverse relation"*
        
        .. image:: ../_images/sql/inv_rel.png
        
        You don't need to create the *inverse relation*, you just created it when you created the
        :ref:`relation`.
    
    **Syntax**:
    
        By default, the *inverse relation path* is::
        
            @packageName_tableName_relationColumnName
            
        where:
        
        * ``@`` is the char used in Genro to begin a *relation* (that is, a :ref:`relation`, an
          :ref:`inverse_relation` or a :ref:`relation_path`. For more information check the
          :ref:`at_char` page)
        * ``packageName`` is the name of the :ref:`package <packages_index>`
        * ``tableName`` is the name of the :ref:`table`
        * ``relationColumnName`` is the name of the :ref:`table_relation_column`
          
            **Example**:
            
            If you have the following :ref:`table_relation_column`::
            
              tbl.column('stud_id',size='22',name_long='Student ID').relation('school.student.id',
                                                                               mode='foreignkey')
              
            where the packageName is "school", the tableName is "student" and the relatedName is "stud_id",
            the automatic ``relation_name`` is::
            
              @school_student_stud_id
              
        You can change the default string of the *inverse relation path* through the :ref:`relation_name`,
        an attribute of the :ref:`table_relation`.
        
            .. _relation_name:

relation_name
-------------

    An attribute of the :ref:`table_relation`. It allows to estabilish an alternative string
    for the :ref:`inverse_relation`.
    
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
                                                                           
        The ``relation_name`` is not anymore ``school_student_stud_id``, but::
        
            @students
            
.. _relation_path:

relation path
=============

    **definition**: the *relation path* is a set of two or more :ref:`relations <relation>`
    and :ref:`inverse relations <inverse_relation>`.
    
    Check the :ref:`path_examples` section for more information.
            
.. _path_examples:

examples
========

.. _path_example_one:

college example
---------------

    Let's describe a small set of :ref:`tables <table>` to explain how the concepts of
    :ref:`relation`, :ref:`inverse_relation` and :ref:`relation_path` work.
    
    We want to describe the registration to some college exams, so we need three tables:
    one for the *students* (we'll call it "S"), one for the *exams* (called "EX") and one for
    the *exam registrations* (called "ER"). The ER table will be linked both to the other two
    tables through two :ref:`relation columns <table_relation_column>`:
    
    #. one relation column will be used for the creation of a relation between the ER table
       and the EX table; so you have available:
    
        * a *relation* to get data from ER to EX
        * an *inverse relation* to get data from EX to ER
        
    #. one relation column will be used for the creation of a relation between the ER table
       and the S table; so you have available:
    
        * a *relation* to get data from ER to S
        * an *inverse relation* to get data from S to ER
        
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
    
    * line 1 - define the environment location of the Python application
    * line 2 - define the encoding
    * lines 4 and 5 - create the ``Table`` class and the ``config_db`` method that
      handles all the stuff about our table
    * line 6 - create the table, specifying its name (``student``) and its primary key (the :ref:`pkey`)
    * line 7 - introduce the :ref:`sysfields` method that allows to create the id column
      (it does other things, too, but they are not important in this example)
    * line 8 - create the ``Name`` :ref:`table_column`, including the students' name
    
    You can find more information on the creation of a table in the :ref:`table` page.
    
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
                
    There aren't differences respect to the student table.
    
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
    * line 9 - we create the :ref:`relation` between the ER table and the S table
    * line 10 - the :ref:`relation_name` specify a different name respect to the standard name
      for the :ref:`inverse_relation` between the ER table and the S table 
    * line 11 - we create the :ref:`relation` between the ER table and the EX table
    * line 12 - the :ref:`relation_name` specify a different name respect to the standard name
      for the :ref:`inverse_relation` between the ER table and the EX table
      
    So we have now this situation:
    
    .. image:: ../_images/sql/path_example_2.png
      
    Let's see how can you get data from a table to another:
    
    * **relations - from ER table to EX table**
      
      The syntax of the direct relation from the ER table to the EX table is:
      
      * for the *name* column::
      
        @exam_id.name
        
        where:
        
        * the :ref:`at_char` is the special character used to specify any relation in Genro
          (relations, inverse relations and relation paths)
        * ``exam_id`` is the name of the :ref:`table_relation_column` from the ER table to the EX table
        * ``name`` is the name of the :ref:`table_column` of the EX table we look for
        
      * for the *professor* column::
            
        @exam_id.professor
        
        this is similar to the previous one.
        
    * **relations - from ER table to S table**
      
      The syntax of the direct relation from the ER table to the S table is:
      
      * for the *name* column::
      
        @stud_id.name
        
        where:
        
        * the :ref:`at_char` is the special character used to specify any relation in Genro
          (relations, inverse relations and relation paths)
        * ``stud_id`` is the name of the :ref:`table_relation_column` from the ER table to the S table
        * ``name`` is the name of the :ref:`table_column` of the S table we look for
        
    * **inverse relations - from EX table to ER table**:
      
      The syntax of the inverse relation from the EX table to the ER table is:
      
      * for the *date* column::
      
        @ex_registrations_date
        
        where:
        
        * the :ref:`at_char` is the special character used to specify any relation in Genro
          (relations, inverse relations and relation paths)
        * ``ex_registrations`` is the name of the :ref:`relation_name` of the ER table
        * ``date`` is the name of the :ref:`table_column` of the ER table we look for
        
      * **inverse relations - from S table to ER table**:
      
      The syntax of the inverse relation from the S table to the ER table is:
      
      * for the *date* column::
      
        @stud_registrations_date
        
        where:
      
        * the :ref:`at_char` is the special character used to specify any relation in Genro
          (relations, inverse relations and relation paths)
        * ``stud_registrations`` is the name of the :ref:`relation_name` of the ER table
        * ``date`` is the name of the :ref:`table_column` of the ER table we look for
        
    * **relation paths (both direct and inverse relations) - from EX table to S table**:
      
      Let's suppose that you are in a page related to the EX table
      and you want to take data from the S table, like in this image:
      
      .. image:: ../_images/sql/path_example_3.png
      
      The path is divided in two steps:
      
      * the first step (the yellow arrow) is an inverse relation between EX and ER tables
      * the second step (the blue arrow) is a direct relation between ER and S tables
      
      So, for the student column "name", the full relation path is::
      
        @ex_registrations.stud_id.name
        
      where:
      
      * the :ref:`at_char` is the special character used to specify any relation in Genro
        (relations, inverse relations and relation paths)
      * ``ex_registrations`` is the name of the :ref:`relation_name` of the ER table
      * ``stud_id.name`` is the direct relation from the ER table to the S table
      
    * **relation paths (both direct and inverse relations) - from S table to EX table**:
      
      Similarly, let's suppose that you are in a page related to the S table
      and you want to take data from the EX table, like in this image:
      
      .. image:: ../_images/sql/path_example_4.png
      
      The path is divided in two steps:

        * the first step (the yellow arrow) is an inverse relation between S and ER tables
        * the second step (the blue arrow) is a direct relation between ER and EX tables
      
      So, for the exam column "name", the full relation path is::
      
        @stud_registrations.exam_id.name
        
      for the exam column "professor", the full relation path is::

        @stud_registrations.exam_id.professor
        
**Footnotes**:

.. [#] More information on these introductory lines in the :ref:`table_creation` section and in the :ref:`table_config_db` section of the :ref:`table` page