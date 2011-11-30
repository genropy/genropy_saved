.. _dbselect_dbcombobox:
	
===========================================
dbSelect and dbCombobox: commons attributes
===========================================
    
    *Last page update*: |today|
    
    * :ref:`db_attributes`
    * :ref:`db_examples_hasdownarrow`
    
.. _db_attributes:

common attributes
=================

    Here we show the attributes that belong both to :ref:`dbselect` than to :ref:`dbcombobox`:
    
    ==================== =================================================== ========================== ======================================
       Attribute                   Description                                  Default                       Example                         
    ==================== =================================================== ========================== ======================================
     *dbtable*            MANDATORY - Select the database                      ``None``                 :ref:`dbtable` explanation page 
                          :ref:`table` for database widget query             
    -------------------- --------------------------------------------------- -------------------------- --------------------------------------
     *alternatePkey*      Alternate primary key: allow to save user choice     ``None``                                                       
                          through a different parameter respect to the                                                                        
                          default ID. You can set any other field's                                                                           
                          parameter as alternatePkey                                                                                          
    -------------------- --------------------------------------------------- -------------------------- --------------------------------------
     *auxColumns*         Show in a pop-up menu below the input textbox        ``None``                 :ref:`dbselect_examples_auxcolumns`   
                          query parameters (*columns* becomes MANDATORY)                                                                      
    -------------------- --------------------------------------------------- -------------------------- --------------------------------------
     *columns*            Additional query fields                              ``None``                 :ref:`dbselect_examples_columns`      
    -------------------- --------------------------------------------------- -------------------------- --------------------------------------
     *condition*          more :ref:`condition` into the query                 ``None``                 :ref:`dbselect_examples_condition`    
    -------------------- --------------------------------------------------- -------------------------- --------------------------------------
     *hasDownArrow*       If True, show an arrow and let the user choose       ``False``                :ref:`db_examples_hasdownarrow`       
                          from all the entries (so, the *limit* attribute                                                                     
                          is overridden                                                                                                       
    -------------------- --------------------------------------------------- -------------------------- --------------------------------------
     *ignoreCase*         If True, allow the user to ignore the case           ``True``                                                       
    -------------------- --------------------------------------------------- -------------------------- --------------------------------------
     *label*              You can't use the *label* attribute; if you          ``None``                 :ref:`lbl_formbuilder` example        
                          want to give a label to your widget, check the                                                                      
                          :ref:`lbl_formbuilder` example                                                                                      
    -------------------- --------------------------------------------------- -------------------------- --------------------------------------
     *limit*              Set the number of visible choices on the pop-up      ``10``                                                         
                          menu below the input textbox during user typing.                                                                    
                          Set *limit* to "0" (``limit=0``) to allow to see                                                                    
                          all the possible values                                                                                             
    -------------------- --------------------------------------------------- -------------------------- --------------------------------------
     *rowcaption*         Allow user to view records through                   ``None``                 :ref:`rowcaption` page                
                          :ref:`name_long` value.                                                                                             
                          Without *rowcaption*, user will see value ID                                                                        
    -------------------- --------------------------------------------------- -------------------------- --------------------------------------
     *selected*           You can add different parameters with the sintax:    ``None``                 :ref:`dbselect_examples_selected`     
                          ``selected_columnName='path'``                                                                                      
    ==================== =================================================== ========================== ======================================
    
.. _db_examples_hasdownarrow:

hasDownArrow example
====================

    If ``True``, the *hasDownArrow* attribute:
    
    #. changes the appearence of the field adding a "down arrow"
    #. bring the *limit* attribute to "0" (so user can scroll through all the possible values)
       
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
                          