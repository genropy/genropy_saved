	.. _genro_field:

=====
field
=====

    * :ref:`field_def`
    * :ref:`field_description`
    * :ref:`field_attributes`
    * :ref:`field_examples`: :ref:`first_one`, :ref:`second_one`, :ref:`third_one`
    
.. _field_def:

Definition
==========

    .. automethod:: gnr.web.gnrwebstruct.GnrDomSrc_dojo_11.field

.. _field_description:

Description
===========

    *field* is used to view and select data included in a database :ref:`packages_model_table` (and, eventually, modify them).

    Its type is inherited from the type of data contained in the table to which *field* refers. For example, if *field* catches data from a :ref:`genro_numbertextbox`, its type is actually a ``numberTextbox``.

    *field* MUST be a child of the :ref:`genro_formbuilder` form widget, and ``formbuilder`` itself MUST have a :ref:`genro_datapath` for inner relative path gears. So, *field* search a form to bind itself to, so don't forget to link every *field* to a ``formbuilder``! Here is an example::
        
        class GnrCustomWebPage(object):
            def main(self,root,**kwargs):
                fb = root.formbuilder(datapath='myPathForData')
                fb.field(...) # The field's content will be explained below...
            
    The last thing is to specify the database table to which the *field* refers to. There are three different possibilities for doing this:
    
    * :ref:`first_one`
    * the :ref:`second_one`
    * :ref:`third_one`
    
.. _field_attributes:

Attributes
==========
    
    **field attributes**:
    
    * *field*: MANDATORY - the field's query path; the complete syntax is ``packageName.tableName.tableAttributeName``. It can be used in a combo with ``dbtable`` (a ``formbuilder`` attribute) and with the ``maintable``
    * *limit*: The max number of rows displayed in a field as response to user request. The last line is always a line with no characters, so user can choose it to not perform his request
    * *lbl*: Set the Field label. Properly, "lbl" is a formbuilder's child attribute, so if you don't specify it, then *field* will inherit it from the :ref:`genro_name_long` attribute of the requested data
    * *rowcaption*: Allow user to view records through the record's :ref:`genro_name_long` value. Check for more information on :ref:`genro_database_rowcaption` page
    * *zoom*: Allow to open the linked record in its :ref:`packages_model_table`. For further details, check the :ref:`genro_zoom` page
    
    **Common attributes**:
    
    * *disabled*: if True, allow to disable this widget. Default value is ``False``. For more information, check the :ref:`genro_disabled` documentation page
    * *hidden*: if True, allow to hide this widget. Default value is ``False``. For more information, check the :ref:`genro_hidden` documentation page
    * *label*: You can't use the *label* attribute; if you want to give a label to your widget, check the :ref:`lbl_formbuilder` example
    * *visible*: if False, hide the widget (but keep a place in the :ref:`genro_datastore` for it). For more information, check the :ref:`genro_visible` documentation page
    
.. _field_examples:

Examples
========

.. _first_one:

dbtable on the formbuilder
==========================

    You can set the ``dbtable`` attribute on the formbuilder, like::
    
        class GnrCustomWebPage(object):
            def main(self,root,**kwargs):
                fb = root.formbuilder(datapath='test1',dbtable='showcase.cast')
                
    where ``showcase`` is the name of the package and ``cast`` is the name of the ``table``. At this point, the field will be like::
    
                fb.field('person_id',rowcaption='$name')
                
    So, the first value of the field contains the name of the attribute you want to save in the :ref:`genro_datastore` (for rowcaption explanation, check :ref:`field_attributes`).

.. _second_one:

maintable
=========

    In this example we show to you that you can introduce the ``maintable`` in the place of the ``formbuilder`` ``dbtable``::
    
        class GnrCustomWebPage(object):
        
            maintable='showcase.cast'
            
            def main(self,root,**kwargs):
                fb = root.formbuilder(datapath='test2')
                fb.field('person_id',rowcaption='$name')
                
    If you have more than one ``formbuilder``, the ``maintable`` is being applied to EVERY ``formbuilder``.
    
.. _third_one:

internal dbtable
================

    In this last case we show that you can set the dbtable inside the field::
    
        class GnrCustomWebPage(object):
            def main(self,root,**kwargs):
                fb = root.formbuilder(datapath='test3')
                fb.field('showcase.cast.person_id',rowcaption='$name')

    In this example, the first *field* attribute (its query-path) has the syntax ``packageName.tableName.tableAttributeName``. Genro trasforms the *field* into a ``dbselect``, splitting the query-path in two: ``packageName.tableName`` will go as the string applied to the ``dbtable`` attribute, while the ``tableAttributeName`` will go as the string applied to the *value* attribute. So, the path of field value will be ``/test1/person_id/ID``, where ``test1`` is the name we chose for the datapath, ``person_id`` is the name of the attribute we chose for user query contained in the database model called ``cast`` and the ID is the record ID.