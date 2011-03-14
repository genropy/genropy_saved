.. _genro_formbuilder:

===========
formbuilder
===========

    * :ref:`formbuilder_def`
    * :ref:`formbuilder_description`
    * :ref:`formbuilder_attributes`
    * :ref:`formbuilder_examples`
    * :ref:`formbuilder_other_features`: :ref:`label_and_lbl`

.. _formbuilder_def:

Definition
===========

    .. automethod:: gnr.web.gnrwebstruct.GnrDomSrc.formbuilder

.. _formbuilder_description:

Description
===========

    The formbuilder simplify the creation of forms.
    
    With formbuilder you have an ordered place to put your HTML object; formbuilder is used in place of an HTML table.
    
    To let you see how Genro code is simpler and more compact, we report here a comparison between an HTML table and a Genro formbuilder::
    
        <!-- HTML code: -->
        <table>
            <tr>
                <td>
                    <input type='text' value='name'/>
                </td>
            </tr>
        </table>
        
        # Genro code:
        fb = root.formbuilder()
        fb.textbox(value='^name',lbl='Name')
    
.. _formbuilder_attributes:

field's Attributes
==================

    The formbuilder supports many attributes for its fields, that are:
    
    * *colspan*: Set the number of columns occupied by a single field. Default value is ``1``
    * *label*: If possible, set a label for formbuilder right field_part (more details on this example_). Default value is ``None``
    * *lbl*: If possible, set a label for formbuilder left field_part (more details on this example_). Default value is ``None``
    * *pos*: Choose element position. The default value is the first free position. The syntax is ``pos(NUMBER,NUMBER)``, whereas the first value represents a row, the second value represents a column. Other feature: "pos" accepts as a number row two special characters::

        ``+`` to refer itself at the following row
        ``*`` to refer itself at the current row

    * *value*: Set a path for formbuilder's values. For more details, see :ref:`genro_datapath`. Default value is ``None``

    **common attributes**:

    * *disabled*: if True, allow to disable this widget. Default value is ``False``. For more information, check the :ref:`genro_disabled` documentation page
    * *hidden*: if True, allow to hide this widget. Default value is ``False``. For more information, check the :ref:`genro_hidden` documentation page
    * *visible*: if False, hide the widget (but keep a place in the :ref:`genro_datastore` for it). For more information, check the :ref:`genro_visible` documentation page

.. _formbuilder_examples:

Examples
========

    Let's see a code example::

        class GnrCustomWebPage(object):
            def main(self,root,**kwargs):
                fb=root.formbuilder(datapath='test3',cols=3,fld_width='100%',width='100%')
                fb.textbox(value='^.name',lbl='Name')
                fb.textbox(value='^.surname',colspan=2,lbl='Surname')
                fb.numberTextbox(value='^.age',lbl="Age")
                fb.dateTextbox(value='^.birthdate',lbl='Birthdate')
                fb.filteringSelect(value='^.sex',values='M:Male,F:Female',lbl='Sex')
                fb.textbox(value='^.job.profession',lbl='Job')
                fb.textbox(value='^.job.company_name',lbl='Company name')
                fb.textbox(value='^.job.fiscal_code',lbl='Fiscal code')

.. _formbuilder_other_features:

Other features
==============

.. _example:

.. _label_and_lbl:

label and lbl: an explanation
=============================

    Every formbuilder column is splitted in two parts (left one and right one): in the left one lie the values of the "lbl" attributes, while in the right one lie the values of the "label" attributes. Usually you label your form's fields with "lbl", excepted for the radiobuttons and the checkboxes on which you have to use "label" (the reason is merely visual).
    
    Example::
    
        class GnrCustomWebPage(object):
            def main(self,root,**kwargs):
                fb = pane.formbuilder(datapath='test2',cols=2)
                fb.textbox(value='^.name',lbl='Name')
                fb.textbox(value='^.surname',lbl='Surname')
                fb.textbox(value='^.job',lbl='Profession')
                fb.numberTextbox(value='^.age',lbl='Age')
                fb.div('Favorite sport:')
                fb.div('Favorite browser:')
                fb.checkbox(value='^.football',label='Football')
                fb.radiobutton('Internet explorer',value='^.radio1',group='genre1')
                fb.checkbox(value='^.basketball',label='Basketball')
                fb.radiobutton('Mozilla Firefox',value='^.radio2',group='genre1')
                fb.checkbox(value='^.tennis',label='Tennis')
                fb.radiobutton('Google Chrome',value='^.radio3',group='genre1')

    To help you in discovering of the formbuilder hidden structure we used the "border" attribute (the outcome doesn't follow the standard of beauty, but the example is instructive!).

    So replacing the line::
    
        fb = pane.formbuilder(datapath='test2',cols=2)
        
    with::
    
        fb = pane.formbuilder(datapath='test2',border='5px',cols=2)

    the effect will be: ??? add online demo...
