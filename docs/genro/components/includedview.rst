.. _genro_includedview:

=============
included view
=============

	* :ref:`iv_description`
	* :ref:`iv_example`
	* :ref:`iv_library_reference`

.. _iv_description:

Description
===========

	Return a grid for viewing and selecting rows from a many to many table related to the main table; also, return a widget that allow to edit data. The form can be contained inside a dialog or a contentPane and is useful to edit a single record.
	The possible specifiers are ``addAction=True`` or ``delAction=True`` to unleash the standard events (records modification in a recordDialog).
	
	<LUPI'S CLIPBOARD>
	
	 In this case, the records are updated in the datastore (ie are treated as logically part of the record in the master table, and the changes will be applied to save the master record).

	The ``gridEditor()`` method allow to define the widgets used for editing lines. (The widgets are reused gridEditor, moving them into the DOM of the page, as you move between the lines.)
	
	</LUPI'S CLIPBOARD>

.. _iv_example:

Example
=======

	::

		def formBase(self, parentBC, disabled=False, **kwargs):
			bc = parentBC.borderContainer(**kwargs)
			pane = bc.contentPane(region='left',width='65%')
			tc = bc.tabContainer(region='center')
			self.wounds_grid(tc.borderContainer(title='!!Wounds'))
			
		def wounds_grid(self,bc):
			iv = self.includedViewBox(bc,
			                          add_action=True,del_action=True,nodeId='WoundsGrid',
			                          editorEnabled=True,storepath='.wounds_base',
			                          struct=self.ferite_struct,datamode='bag',label='!!Wounds')
			
			gridEditor = iv.gridEditor()
			gridEditor.numberTextbox(gridcell='from')
			gridEditor.numberTextbox(gridcell='to')
			gridEditor.numberTextbox(gridcell='value')
			
		def ferite_struct(self, struct):
			r = struct.view().rows()
			r.cell('da',name='Tiro da',dtype='L',width='3em')
			r.cell('a',name='Tiro a',dtype='L',width='3em')
			r.cell('valore',name='Valore',dtype='L',width='7em')

.. _iv_library_reference:

Included view library reference
===============================

	For the complete IncludedView library reference, check the :ref:`genro_library_includedview` page.
	