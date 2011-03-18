.. _genro_includedview:

============
includedView
============

    .. warning:: completely to rewrite!! add???
    
    * :ref:`iv_description`
    * :ref:`iv_example`
    * :ref:`iv_library_reference`

.. _iv_description:

Description
===========

    Return a grid for viewing and selecting rows from a many to many table related to the main table; also,
    return a widget that allow to edit data. The form can be contained inside a dialog or a contentPane and
    is useful to edit a single record. The possible specifiers are ``addAction=True`` or ``delAction=True``
    to unleash the standard events (records modification in a recordDialog).
    
    ::
    
        <LUPI'S CLIPBOARD>
        
            In this case, the records are updated in the datastore (ie are treated as logically part of the record
            in the master table, and the changes will be applied to save the master record).
            
            The ``gridEditor()`` method allow to define the widgets used for editing lines. (The widgets are reused
            gridEditor, moving them into the DOM of the page, as you move between the lines.)
            
            The includedView is well documented. Some parameters such as ``formPars`` and ``pickerPars`` are deprecated
            but (now there is another way to do the same thing.)
            
            The possible specifiers are ``addAction=True`` or ``delAction=True`` to unleash the standard events
            (modification of records in a recordDialog). In this case, the records are updated in the datastore
            (ie are treated as logically part of the record in the master table, and the changes will be applied
            to save the master record).
            
            Using the method ``iv.gridEditor()`` can define the widgets used for editing lines. (The widgets are
            reused gridEditor, moving them into the DOM of the page, as you move between the lines.)
            
            includedViewBox:
                list of records useful for implementing views master / detail
        
        </LUPI'S CLIPBOARD>
        
.. _iv_searchbox:

searchBox
---------

    add???
    
.. _iv_searchon:

searchOn
--------

    add???
    
.. _iv_messageBox:

messageBox
----------

    add???
    
.. _iv_example:

Example
=======

    add???

.. _iv_library_reference:

includedView library reference
==============================

    For a complete IncludedView library reference, check the :ref:`genro_library_includedview` page.