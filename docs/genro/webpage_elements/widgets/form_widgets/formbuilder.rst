.. _formbuilder:

===========
formbuilder
===========
    
    *Last page update*: |today|
    
    * :ref:`formbuilder_def`
    * :ref:`formbuilder_attributes`:
    
        * :ref:`formbuilder_children_attributes`
        * :ref:`fb_kwargs`
        * :ref:`formbuilder_prefixes`
        
    * :ref:`fb_examples_label_lbl`
    * :ref:`fb_examples`:
    
        * :ref:`fb_examples_simple`
        * :ref:`fb_examples_label_lbl`
        * :ref:`fb_examples_attributes`
        
.. _formbuilder_def:

definition
==========

    .. automethod:: gnr.web.gnrwebstruct.GnrDomSrc.formbuilder
    
    **Example**::
    
        class GnrCustomWebPage(object):
            def main(self, root, kwargs):
                fb = root.formbuilder(datapath='test')
                fb.textbox(value='^.name',lbl='First Label')
                fb.textbox(value='^.surname',lbl='Second Label')
                
.. _formbuilder_attributes:

attributes
==========

.. _formbuilder_children_attributes:

formbuilder's fields attributes
-------------------------------

    The formbuilder supports many attributes for its fields, that are:
    
    * *colspan*: Set the number of columns occupied by a single child. Default value is ``1``
    * *label*: If possible, set a label for formbuilder right field_part (more details on this
      :ref:`example <fb_examples_label_lbl>`). Default value is ``None``
    * *lbl*: If possible, set a label for formbuilder left field_part (more details on this
      :ref:`example <fb_examples_label_lbl>`). Default value is ``None``
    * *pos*: Choose element position. The default value is the first free position. The syntax is
      ``pos(NUMBER,NUMBER)``, whereas the first value represents a row, the second value represents a column.
      Other feature: "pos" accepts as a number row two special characters::
      
        ``+`` to refer itself at the following row
        ``*`` to refer itself at the current row
        
    * *value*: Set a path for formbuilder's values. For more details, see :ref:`datapath`.
      Default value is ``None``
      
.. _fb_kwargs:

kwargs list
-----------

    The formbulder accepts every :ref:`css` and :ref:`css3` attribute. We list here some
    additional attributes and some css attributes that have a default value in the formbuilder:
    
    * *border_spacing*: define the space between form fields. Default value is ``6px``
    * *datapath*: set the root's path of formbuilder's fields. For more details,
      check the :ref:`datapath` documentation page
    * *width*: define the formbuilder width. You can use a width in pixel, em, ex.
      You can use a percentage, too (e.g: ``width='60%'``), if the formbuilder is a child of a
      :ref:`contentpane` or a div with a defined width and height
      
.. _formbuilder_prefixes:

CSS attributes
--------------
      
    There also 5 prefixes that allow to define the dimensions of every formbuilder part.
    They can be used in combo with any :ref:`css` expression.
    
    In order to understand the usage of the 5 prefixes, keep in mind the conversion of the
    formbuilder structure into the HTML (we saw it at the beginning of the page)
    
    Let's see now the 5 attributes:
    
    * *fld_* + *CSS attribute*: set a CSS expression to every field.
      (e.g: fld_color='red', fld_width='100%')
      
    * *lbl_* + *CSS attribute*: set a CSS expression to every label.
      (e.g: lbl_width='10em')
      
    * *row_* + *CSS attribute*: set a CSS expression to every row
      
    * *tdf_* + *CSS attribute*: set a CSS expression to every <td></td> tag associated
      to a formbuilder's field
      
    * *tdl_* + *CSS attribute*: set a CSS expression to every <td></td> tag associated
      to a formbuilder's label
      
.. _fb_examples:

examples
========

.. _fb_examples_simple:

simple example
--------------

    * `formbuilder [basic] <http://localhost:8080/webpage_elements/widgets/form_widgets/formbuilder/1>`_
    * **Description**: how to fill a comboBox through "values" attribute
      
      .. note:: 
                
                Example elements' list:
                
                   * **classes**: :ref:`gnrcustomwebpage`
                   * **components**: :ref:`testhandlerfull`
                   * **webpage variables**: :ref:`webpages_py_requires`
                   * **widgets**: :ref:`datetextbox`, :ref:`filteringselect`, :ref:`numbertextbox`, :ref:`textbox`
                   
    * **Code**::
    
        # -*- coding: UTF-8 -*-
        """formbuilder"""

        class GnrCustomWebPage(object):
            py_requires = "gnrcomponents/testhandler:TestHandlerFull"

            def test_1_basic(self, pane):
                """Basic formbuilder"""
                fb = pane.formbuilder(cols=2)
                fb.textbox(value='^.name', lbl='Name')
                fb.textbox(value='^.surname', lbl='Surname')
                fb.numberTextbox(value='^.age', lbl="Age")
                fb.dateTextbox(value='^.birthdate', lbl='Birthdate')
                fb.filteringSelect(value='^.sex', values='M:Male,F:Female', lbl='Sex')
                fb.textbox(value='^.job.profession', lbl='Job')
                fb.textbox(value='^.job.company_name', lbl='Company name')
                
.. _fb_examples_label_lbl:

label and lbl example
---------------------

    * `formbuilder [label/lbl] <http://localhost:8080/webpage_elements/widgets/form_widgets/formbuilder/2>`_
    * **Description**: most of the elements supports only the "lbl" attribute.
      
      The rule is: in the formbuilder you have to use the "lbl" attribute to specify
      the label, except for:
      
      * the :ref:`radiobuttons <radiobutton>`
      * the :ref:`checkboxes <checkbox>`
      
      in which you have to use the "label" attribute
      
      .. note:: 
      
                Example elements' list:
                
                   * **classes**: :ref:`gnrcustomwebpage`
                   * **components**: :ref:`testhandlerfull`
                   * **webpage variables**: :ref:`webpages_py_requires`
                   * **widgets**: :ref:`checkbox`, :ref:`datetextbox`, :ref:`radiobutton`, :ref:`textbox`
                   
    * **Code**::
    
        # -*- coding: UTF-8 -*-
        """formbuilder"""

        class GnrCustomWebPage(object):
            py_requires = "gnrcomponents/testhandler:TestHandlerFull"
            
            def test_2_lbl_label(self, pane):
                fb = pane.formbuilder(datapath='test2',cols=2)
                fb.div('The next fields have the \"lbl\" attribute:', colspan=2)
                fb.textbox(value='^.name', lbl='Name')
                fb.textbox(value='^.surname', lbl='Surname')
                fb.textbox(value='^.job', lbl='Profession')
                fb.numberTextbox(value='^.age', lbl='Age')
                fb.div('The next fields have the \"label\" attribute:', colspan=2)
                fb.div('Favorite sport:')
                fb.div('Favorite browser:')
                fb.checkbox(value='^.football',label='Football')
                fb.radiobutton(label='Internet explorer',value='^.radio.IE',group='genre1')
                fb.checkbox(value='^.basketball',label='Basketball')
                fb.radiobutton('Mozilla Firefox',value='^.radio.firefox',group='genre1')
                fb.checkbox(value='^.tennis',label='Tennis')
                fb.radiobutton('Google Chrome',value='^.radio.chrome',group='genre1')
            
.. _fb_examples_attributes:

attributes example
------------------

    * `formbuilder [attributes] <http://localhost:8080/webpage_elements/widgets/form_widgets/formbuilder/3>`_
    * **Description**: check the code for the usage of the most common attributes
      
      .. note:: 
                
                #. Example elements' list:
                
                   * **classes**: :ref:`gnrcustomwebpage`
                   * **components**: :ref:`testhandlerfull`
                   * **webpage variables**: :ref:`webpages_py_requires`
                   * **widgets**: :ref:`datetextbox`, :ref:`dbselect`, :ref:`filteringselect`,
                     :ref:`numbertextbox`, :ref:`textbox`,
                     
    * **Code**::
    
        # -*- coding: UTF-8 -*-
        """formbuilder"""

        class GnrCustomWebPage(object):
            py_requires = "gnrcomponents/testhandler:TestHandlerFull"
            
            def test_3_attributes(self, pane):
                pane.div('We introduce here the most common attributes of the formbuilder:', margin_left='6em')
                pane.div("""fb = pane.formbuilder(cols=2, lbl_width=\'8em\',
                            fld_width=\'15em\', lbl_color=\'teal\')""", margin_left='6em')
                fb = pane.formbuilder(cols=2, lbl_width='6em', fld_width='15em', lbl_color='gray')
                fb.textbox(value='^.name', lbl='Name')
                fb.textbox(value='^.surname', lbl='Surname')
                fb.numberTextbox(value='^.age', lbl="Age")
                fb.dateTextbox(value='^.birthdate', lbl='Birthdate')
                fb.filteringSelect(value='^.sex', values='M:Male,F:Female', lbl='Sex')
                fb.textbox(value='^.job.profession', lbl='Job')
                fb.textbox(value='^.job.company_name', lbl='Company name')
                fb.dbSelect(dbtable='showcase.person', value='^.artist', lbl='Favorite artist', hasDownArrow=True)
                