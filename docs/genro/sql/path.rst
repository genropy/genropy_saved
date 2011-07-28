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
    
    1. create in your :ref:`table` the following introductory lines::
    
        #!/usr/bin/env python
        # encoding: utf-8
        
        class Table(object):
            def config_db(self, pkg):
            
    2. in the ``config_db`` method you have attach to the pkg object the table::
    
        tbl = pkg.table('exam',pkey='id',name_long='Exam',name_plural='Exams')
        
    You can get more information on the points 1 and 2 in the :ref:`table` documentation page.
        
    3. then you have to create a :ref:`table_column` linked to the id of the table you want to link::
       
        tbl.column('stud_id',size='22',name_long='Student ID')
        
    where:
    
    * ``stud_id`` is an arbitrary name for the relation column, that is a column through which you have
      made the relation
    * ``size`` is the column lenght; we put ``22`` because the ID lenght is 22
    * ``name_long`` is used for the visualization of the column in the :ref:`webpages <webpages_webpages>`
      (more information :ref:`here <name_long>`)
      
    4. to the ``stud_id`` column you have to attach a ``relation`` method::
    
        tbl.column('stud_id',size='22',name_long='Student ID').relation('school.student.id',mode='foreignkey')
        
    where:
    
    * ``student.id`` is a string composed by the name of the package that includes the table to relate
      (``school``), the name of the table to relate (``student``) and its :ref:`pkey` (``id``)
    * ``mode='foreignkey'``is a string that transform the relation in a SQL relation
    
    You can get more information on the point 3 in the example :ref:`below <path_example_one>` and in the
    definition of the ``relation`` method :ref:`here <table_relation>`.
    
.. _relation_path:

relation path
=============

    **Definition**:
    
        A relation path is a walk through the connection established between two tables made in the
        direct direction, that is the direction from the table in which you have created the relation
        to the table related.
        
        If you want to walk in the inverse direction, that is from the table related to the table in
        which you have created the relation, we talk about :ref:`inv_rel_path`.
    
    **Syntax**:
    
        To create a relation path you have to append the ``relation`` method to a column that is
        linked to the id of the table to which you want to create the link. Check
        :ref:`here <table_relation>` for more information about the relation method.
        
        add??? Explain the "@" and the "." syntax!
    
.. _inv_rel_path:

inverse relation path
=====================

    **Definition**:
    
    An inverse relation path is a walk through the connection established between two tables made
    in the inverse direction, that is the direction from the table related to the table in which
    you have created the relation.
    
    To create an *inverse relation path*, you have to define a :ref:`relation_name`
    
.. _relation_name:

relation_name
-------------

    An attribute of the :ref:`table_relation`. It allows to define the :ref:`inv_rel_path`.
    
    un path di relazione inverso permette di risalire un path di relazione diretta AL CONTRARIO.
    Se non specificato altrimenti la sintassi di questo path è::
    
        nomePackage_nomeTable_NomeDellaForeignKey
        
    con NomeDellaForeignKey si intende il nome della column con cui si è creata la relazione.
    
    es::
    
        polimed_specialita_medico_medico_id
        
    (package=polimed;nomeTable='specialita_medico';nomeForeignKey='medico_id')
    
    Si può specificare una sintassi alternativa con il relation_name
    
    **Syntax**:
    
        add???
    
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
      
    Let's see now how can we pass from a table to another table:
    
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
    
    
      
    
    