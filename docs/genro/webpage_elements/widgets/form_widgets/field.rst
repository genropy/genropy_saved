.. _field:

=====
field
=====
    
    *Last page update*: |today|
    
    .. note:: field features:
              
              * **Type**: :ref:`Genro form widget <genro_widgets>`
              * **Common attributes**: check the :ref:`attributes_index` section
              
    * :ref:`field_def`:
    
        * :ref:`field_dbtable_formbuilder`
        * :ref:`the maintable <field_maintable>`
        * :ref:`field_dbtable_field`
    
    * :ref:`field_conversion`
    * :ref:`field_attr`:
    
        * :ref:`field_attr_field`
        
    * :ref:`field_examples`
    
.. _field_def:

definition
==========

    .. automethod:: gnr.web.gnrwebstruct.GnrDomSrc_dojo_11.field
    
    Here is an example::
        
        class GnrCustomWebPage(object):
            def main(self,root,**kwargs):
                fb = root.formbuilder(datapath='myPathForData')
                fb.field(...) # The field's content will be explained below...
                
.. _field_conversion:

field conversion
================

    CLIPBOARD::
    
        elif dtype in ('A', 'T') and fieldobj.attributes.get('values', False):
            result['tag'] = 'filteringselect'
            result['values'] = fieldobj.attributes.get('values', [])
        elif dtype == 'A':
            result['maxLength'] = size
            result['tag'] = 'textBox'
            result['_type'] = 'text'
            result['_guess_width'] = '%iem' % (int(size * .7) + 2)
        elif dtype == 'B':
            result['tag'] = 'checkBox'
            if 'autospan' in kwargs:
                kwargs['colspan'] = kwargs['autospan']
                del kwargs['autospan']
        elif dtype == 'T':
            result['tag'] = 'textBox'
            result['_guess_width'] = '%iem' % int(size * .5)
        elif dtype == 'R':
            result['tag'] = 'numberTextBox'
            result['width'] = '7em'
        elif dtype == 'N':
            result['tag'] = 'numberTextBox'
            result['_guess_width'] = '7em'
        elif dtype == 'L' or dtype == 'I':
            result['tag'] = 'numberTextBox'
            result['_guess_width'] = '7em'
        elif dtype == 'D':
            result['tag'] = 'dateTextBox'
            result['_guess_width'] = '9em'
        elif dtype == 'H':
            result['tag'] = 'timeTextBox'
            result['_guess_width'] = '7em'
        else:
            result['tag'] = 'textBox'
            
.. _field_attr:

Attribute explanation
=====================

.. _field_attr_field:

field attribute
---------------

    The first parameter of the field widget is called "field". It is MANDATORY, and it is the column name
    to which field refers to. The complete syntax is::
    
        packageName.tableName.columnName
        
    but if you are in a webpage related to the same table of the column to which the field is related,
    you can write::
    
        columnName
        
    If you want, you can avoid to write ``packageName.tableName`` even when it is necessary specifying
    the *dbtable* attribute or using the *maintable* webpage variable:
    
    #. :ref:`field_dbtable_formbuilder`
    #. :ref:`the maintable <field_maintable>`
    #. :ref:`field_dbtable_field`
    
.. _field_dbtable_formbuilder:

*dbtable* on the formbuilder
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

    You can set the :ref:`dbtable` attribute on the :ref:`formbuilder`::
    
        class GnrCustomWebPage(object):
            def main(self,root,**kwargs):
                fb = root.formbuilder(datapath='test1',dbtable='showcase.cast')
                
    where ``showcase`` is the name of the package and ``cast`` is the name of the ``table``.
    At this point, the field will be like::
                
                fb.field(field='person_id')
                
    So, the first value of the field contains the name of the attribute you want to save in
    the :ref:`datastore` (for rowcaption explanation, check :ref:`field_attributes`)
    
.. _field_maintable:

maintable
^^^^^^^^^

    In this example we show to you that you can introduce the ``maintable`` in the place of the ``formbuilder`` ``dbtable``::
    
        class GnrCustomWebPage(object):
        
            maintable='showcase.cast'
            
            def main(self,root,**kwargs):
                fb = root.formbuilder(datapath='test2')
                fb.field(field='person_id')
                
    If you have more than one ``formbuilder``, the ``maintable`` is being applied to EVERY ``formbuilder``.

.. _field_dbtable_field:

internal dbtable
^^^^^^^^^^^^^^^^

    In this last case we show that you can set the dbtable inside the field::
    
        class GnrCustomWebPage(object):
            def main(self,root,**kwargs):
                fb = root.formbuilder(datapath='test3')
                fb.field(field='showcase.cast.person_id')

    In this example, the first ``field`` attribute (its query-path) has the syntax
    ``packageName.tableName.tableAttributeName``. Genro trasforms the ``field`` into a ``dbselect``,
    splitting the query-path in two: ``packageName.tableName`` will go as the string applied to the
    *dbtable* attribute, while the ``tableAttributeName`` will go as the string applied to the *value*
    attribute. So, the path of field value will be ``/test1/person_id/ID``, where ``test1`` is the
    name we chose for the datapath, ``person_id`` is the name of the attribute we chose for user
    query contained in the database model called ``cast`` and the ID is the record ID
    
.. _field_examples:

Examples
========

    TODO