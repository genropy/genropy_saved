.. _paths:

=====
paths
=====

    *Last page update*: |today|
    
    * :ref:`relation_path`
    * :ref:`inv_rel_path`
    * :ref:`path_examples`: :ref:`path_example_one`
    
.. _relation_path:

relation path
=============

    You can create relations between database :ref:`tables <table>`.
    
    To create a relation path you have to append the ``relation`` method to a column that is linked
    to the id of the table to which you want to create the link.
    
    add??? Explain the "@" and the "." syntax!
    
    add??? image!
    
.. _inv_rel_path:

inverse relation path
=====================

    CLIPBOARD about the relation_name::
    
        un path di relazione inverso permette di risalire un path di relazione diretta AL CONTRARIO.
        Se non specificato altrimenti la sintassi di questo path è::
        
            nomePackage_nomeTable_NomeDellaForeignKey
            
        con NomeDellaForeignKey si intende il nome della column con cui si è creata la relazione.
        
        es::
        
            polimed_specialita_medico_medico_id
            
        (package=polimed;nomeTable='specialita_medico';nomeForeignKey='medico_id')
        
        Si può specificare una sintassi alternativa con il relation_name
        
    add??? image!
    
.. _path_examples:

Examples
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
    * line 10 - the *relation_name* is an attribute that create the :ref:`inv_rel_path` between
      the *student* table and the *exam registration*
    * line 11 - we create the :ref:`relation_path` between the *exam* table and the *exam registration*
    * line 12 - the *relation_name* is an attribute that create the :ref:`inv_rel_path` between
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
    
    
      
    
    