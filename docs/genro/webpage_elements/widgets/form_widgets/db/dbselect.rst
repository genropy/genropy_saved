.. _dbselect:

========
dbSelect
========
    
    *Last page update*: |today|
    
    .. note:: dbSelect features:
              
              * **Type**: :ref:`Genro form widget <genro_widgets>`
              * **Common attributes**: you can check:
              
                * the :ref:`widget common attributes section <attributes_index>`
                * the :ref:`dbSelect and dbCombobox common attributes section <db_attributes>`
              
    * :ref:`dbselect_def`
    * :ref:`dbselect_examples`:
    
        * :ref:`dbselect_examples_simple`
        * :ref:`dbselect_examples_auxcolumns`
        * :ref:`dbselect_examples_selected`
        * :ref:`dbselect_examples_condition`
        * :ref:`dbselect_examples_columns`
        
.. _dbselect_def:

Definition and Description
==========================

    .. automethod:: gnr.web.gnrwebpage_proxy.apphandler.GnrWebAppHandler.dbSelect
    
    Please check the :ref:`dbselect_examples_simple` below for a deeper description of the
    dbSelect main attributes
    
.. _dbselect_examples:

Examples
========

.. _dbselect_examples_simple:

simple example
--------------

    * `dbSelect [basic] <http://localhost:8080/webpage_elements/widgets/form_widgets/dbSelect/1>`_
    * **Description**: a basic example of a dbSelect.
      
      * The *dbtable* specify the :ref:`database table <table>` from which user chooses the record.
        To define a default ``dbtable`` value for all the elements of your page that supports
        it you can use the :ref:`webpage variable <webpages_variables>` called :ref:`maintable`.
        Clearly, if you define a *dbtable* attribute in a object, it prevails on the *maintable*
        (more information in the :ref:`dbtable` section)
        
      .. note:: example elements' list:
      
                * **classes**: :ref:`gnrcustomwebpage`
                * **components**: :ref:`testhandlerfull`
                * **webpage variables**: :ref:`webpages_py_requires`
                * **widgets**: :ref:`formbuilder`
                
    * **Code**::
    
        # -*- coding: UTF-8 -*-
        """dbSelect"""

        class GnrCustomWebPage(object):
            py_requires = "gnrcomponents/testhandler:TestHandlerFull"

            def test_1_db(self, pane):
                """Basic dbSelect"""
                fb = pane.formbuilder(cols=3)
                fb.div("""In this test you can see the basic funcionalities of the dbSelect attribute:
                          the "dbtable" attribute allows to search from a database table, saving the
                          ID of the chosen record.""", colspan=3)

                fb.div('saved in \"test/test_1_db/id\"')
                fb.dbSelect(dbtable='showcase.person', value='^.id', limit=10)
                fb.div("""dbSelect default attributes: limit=10,
                                                       hasDownArrow=False,
                                                       ignoreCase=True""")

                fb.div('saved in \"test/test_1_db/id2\"')
                fb.dbSelect(dbtable='showcase.person', value='^.id2', hasDownArrow=True)
                fb.div("""The hasDownArrow=True override the limit=10,
                          and let the user see all the entries""")
                          
.. _dbselect_examples_auxcolumns:

auxColumns example
------------------

    * `dbSelect [auxColumns] <http://localhost:8080/webpage_elements/widgets/form_widgets/dbSelect/2>`_
      
      .. note:: example elements' list:
      
                * **classes**: :ref:`gnrcustomwebpage`
                * **components**: :ref:`testhandlerfull`
                * **webpage variables**: :ref:`webpages_py_requires`
                * **widgets**: :ref:`formbuilder`
                
    * **Code**::
    
        # -*- coding: UTF-8 -*-
        """dbSelect"""

        class GnrCustomWebPage(object):
            py_requires = "gnrcomponents/testhandler:TestHandlerFull"
            
            def test_2_auxcolumns(self, pane):
                """\"auxColumns\" attribute"""
                fb = pane.formbuilder(cols=2)
                fb.div('With \"auxColumns\" attribute you let user see more columns during selection')
                fb.dbSelect(dbtable='showcase.person', value='^.person_id', hasDownArrow=True,
                            auxColumns='$nationality,$b_year')
                            
.. _dbselect_examples_selected:

selected example
----------------

    * `dbSelect [selected] <http://localhost:8080/webpage_elements/widgets/form_widgets/dbSelect/3>`_
    * **Description**: the "selected" attribute allow to save in the :ref:`datastore` more :ref:`columns`
      respect to the standard column taken, that is the id column
      
      The syntax is::
      
        selected_COLUMNNAME='STORE_ADDRESS'
        
      Where:
      
      * COLUMNNAME is the name of a single column
      * STORE_ADDRESS is the path in datastore for the column
      
      .. note:: example elements' list:
      
                * **classes**: :ref:`gnrcustomwebpage`
                * **components**: :ref:`testhandlerfull`
                * **webpage variables**: :ref:`webpages_py_requires`
                * **widgets**: :ref:`formbuilder`
                
    * **Code**::
    
        # -*- coding: UTF-8 -*-
        """dbSelect"""

        class GnrCustomWebPage(object):
            py_requires = "gnrcomponents/testhandler:TestHandlerFull"
        
            def test_3_selected(self, pane):
                """\"selected\" attribute"""
                fb = pane.formbuilder()
                fb.div("""If you want to keep in the datastore some attributes of the chosen record
                          (in addition to the ID), you have to use the "selected" attribute""",colspan=3)
                fb.div("""In this example you get the column \"name\" and the column \"b_year\" and set
                          their value in a custom path. In particular we put the content of the
                          \"nationality\" column in \"test/test_3_selected/nationality\" and the
                          content of the \"b_year\" column in \"test/test_3_selected/year\". You can
                          see them in datastore (ctrl+shift+D), but you can see them even in the
                          two \"readOnly\" fields""",colspan=3)
                fb.dbSelect(lbl='musician', dbtable='showcase.person', value='^.id',
                            selected_nationality='.nationality', selected_b_year='.year')
                fb.textbox(lbl='nationality', value='^.nationality', readOnly=True)
                fb.textbox(lbl='birth year', value='^.year', readOnly=True)
                            
.. _dbselect_examples_condition:

condition example
-----------------

    * `dbSelect [condition] <http://localhost:8080/webpage_elements/widgets/form_widgets/dbSelect/4>`_
      
      .. note:: example elements' list:
      
                * **classes**: :ref:`gnrcustomwebpage`
                * **components**: :ref:`testhandlerfull`
                * **webpage variables**: :ref:`webpages_py_requires`
                * **widgets**: :ref:`formbuilder`
                
    * **Code**::
    
        # -*- coding: UTF-8 -*-
        """dbSelect"""

        class GnrCustomWebPage(object):
            py_requires = "gnrcomponents/testhandler:TestHandlerFull"
            
            def test_4_condition(self, pane):
                """\"condition\" attribute"""
                fb = pane.formbuilder()
                fb.div("""If you have two or more database tables in relation,
                          you can allow the user to choose a record with a first "dbSelect"... """)
                fb.dbSelect(dbtable='showcase.person', value='^.person_id', lbl='Musician',
                            selected_name='.name', selected_b_year='.b_year')
                fb.div("""... and then you can make the user choose an attribute relative to the
                        first record selected through a second dbSelect:""")
                fb.dbSelect(dbtable='showcase.person_music', value='^.music_id', lbl='Music',
                            condition='$person_id=:pid', condition_pid='=.person_id',
                            alternatePkey='music_id')
                            
.. _dbselect_examples_columns:

columns example
---------------

    * `dbSelect [columns] <http://localhost:8080/webpage_elements/widgets/form_widgets/dbSelect/5>`_
      
      .. note:: example elements' list:
      
                * **classes**: :ref:`gnrcustomwebpage`
                * **components**: :ref:`testhandlerfull`
                * **webpage variables**: :ref:`webpages_py_requires`
                * **widgets**: :ref:`formbuilder`
                
    * **Code**::
    
        # -*- coding: UTF-8 -*-
        """dbSelect"""

        class GnrCustomWebPage(object):
            py_requires = "gnrcomponents/testhandler:TestHandlerFull"
            
            def test_5_columns(self, pane):
                """\"columns\" attribute"""
                fb = pane.formbuilder()
                fb.div("""The \"columns\" attribute allows user to search respect to all the fields
                          you specify in it. In this example we specify both \"name\" and \"nationality\",
                          so try to look for an actor respect its name or its nationality (you can try
                          \"Czech\", \"German\" or \"Austrian\", for example)""")
                fb.dbSelect(dbtable='showcase.person', value='^.value',
                            columns='$name,$nationality', auxColumns='$name,$nationality,$b_year,$d_year')
                            