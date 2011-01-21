.. _genro_selectionhandler:

=================
selection handler
=================

* :ref:`selhandler_description`

* :ref:`selhandler_example`

* :ref:`selhandler_library_reference`

.. _selhandler_description:

Description
===========

<CLIPBOARD>
	
	A component that displays records in a grid and allows for modification via a dialog.
	
	:param bc:          borderContainer -- parent
	:param nodeId:      string
	
	    - the dialog ID will be *nodeId* + ``_dlg``
	    - the form ID will be *nodeId* + ``_form``
	
	:param table:       table name
	:param datapath:    datapath
	:param struct:      struct or callable
	:param label:       string or callable
	:param selectionPars:       dict -- selection parameters
	:param dialogPars:          dict -- dialog parameters
	:param reloader:            datapath
	:param externalChanges:
	:param hiddencolumns:
	:param custom_addCondition:
	:param custom_delCondition:
	:param askBeforeDelete:
	:param checkMainRecord:
	:param onDeleting:
	:param dialogAddRecord:
	:param onDeleted:
	:param add_enable:
	:param del_enable:
	:param parentSave:
	:param parentId:
	:param parentLock:
	:param kwargs:
	
Datastore
*********

	Relative to the ``datapath``.
	
	``.reload``
	    Use FIRE to reload data from the server (internally uses FIRE to reload data from the server?? #JBE)
	
	``.status.locked``
	    state of the lock (see parameter ``parentLock`` )
	
	``.selection``
	    current selection, the various rows of the grid
	
	``.dlg``
	    data for the ``recordDialog``
	
	``.dlg.record``
	    the current record
	
	``.selectedId``
	    currently selected item. Has all the attributes in the columns of the current record (you can switch to ``hiddenColumns`` ``selectionhandler ()`` to add other columns).
	
	``.struct``
	    Structure of the grid. Can be changed at run-time to add, remove or edit columns.
	
	``.can_add`` e ``.can_del``
	    Boolean flag (treat as read-only, read the code of the component to see how to edit).
	
Names
*****
	
	Given a ``NodeID`` equal to ``foo``, the various components are named as follows:
	
	    * ``foo_frm`` for the form
	    * ``foo_dlg`` nodeId of the dialog box
	
</CLIPBOARD>

.. _selhandler_example:

Example
=======

.. _selhandler_library_reference:

SelectionHandler library reference
==================================

	For the complete SelectionHandler library reference, check the :ref:`genro_library_selectionhandler` page.
