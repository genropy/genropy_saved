	.. _genro-includedview:

==============
 includedView
==============

 - APPUNTI LUPI
 - DOCUMENTAZIONE ALL'INTERNO DEL FILE
 - DEFINIZIONE
 - MIEI APPUNTI

 APPUNTI LUPI

The includedView is well documented. Some parameters such as ``formPars`` and ``pickerPars`` are deprecated but (now there is another way to do the same thing.)

The possible specifiers are ``addAction=True`` or ``delAction=True`` to unleash the standard events (modification of records in a recordDialog). In this case, the records are updated in the datastore (ie are treated as logically part of the record in the master table, and the changes will be applied to save the master record).

Using the method ``iv.gridEditor()`` can define the widgets used for editing lines. (The widgets are reused gridEditor, moving them into the DOM of the page, as you move between the lines.)

 DOCUMENTAZIONE ALL'INTERNO DEL FILE includedview.py
 	This method returns a grid (includedView) for viewing and selecting rows from a many
 to many table related to the main table, and the widget that allow to edit data.
 You can edit data of a single row (record) using a form (formPars), or pick some rows
 from another table with the picker widget (pickerPars).
 The form can be contained inside a dialog or a contentPane and is useful to edit a single record.
 If the data is stored inside another table you should use the picker to select the rows from that table.
 
 @param parentBC: MANDATORY - parentBC is a border container that you must pass to includedViewBox;
                              it contains the includedView and its labels.
 @param table:
 @param datapath:
 @param storepath: if it is relative what is the datapath?
 @param selectionPars:
 @param formPars (dict): it contains all the params of the widget that host the form.
                     List of params:
                     - mode: "dialog"/"pane" (default is "dialog").
                     - height: height of the dialog.
                     - width: width of the dialog.
                     - formCb: MANDATORY - callback method used to create form.
                               formCb's params:
                                      - formBorderCont: a borderContainer used as root for construction.
                                      - datapath: the correct datapath for data contained into the form.
                                      - region: 'center' of the pane/borderContainer where you place it into.
                     - toolbarHandler: OPTIONAL - a callback for the form toolbar.
                     - title: MANDATORY - for mode dialog
                     - pane: OPTIONAL - pane of the input form
 @param label (string): allow to create a label for the includedView.
 @param add_action (boolean): allow the insertion of a row in the includedView.
 @param add_class: css class of add button.
 @param add_enable: a path to enable/disable add action.
 @param del_action (boolean): allow the deleting of a row in the includedView.
 @param del_class: css class of delete button.
 @param del_enable: a path to enable/disable del action.
 @param close_action (boolean): adding closing button in tooltipDialog.
 @param close_class: css class of close button.
 @param filterOn (boolean, only for picker): allow the filter into the picker grid.
 @param pickerPars (dict): it contains all the params of the tooltip dialog which host the picker grid.
                     List of params:
                     - height: height of the tooltipdialog.
                     - width: width of the tooltipdialog.
                     - label: label of the tooltipdialog.
                     - table: MANDATORY - the table of the picker grid. From this table you can pick
                                          a row for the many to many table you handle.
                     - columns: MANDATORY - columns of the picker grid.
                     - nodeId: MANDATORY - id for the picker.
                     - autowidth, storepath, etc grid params.
                     - filterOn: the columns on which to apply filter.
 @param fromPicker_target_fields: allow to bind the picker's table.
                   columns to the includedView columns of the many to many table.
 @param fromPicker_nodup_field: if this column value is present in the includedView it allows
                                to replace that row instead of adding a duplicate row.
 @params kwargs: you have to put the includedView params: autowidth, storepath, etc.




 DEFINIZIONE

	def includedViewBox(self,parentBC,nodeId=None,table=None,datapath=None,
	                    storepath=None,selectionPars=None,formPars=None,label=None,footer=None,
	                    add_action=None,add_class='buttonIcon icnBaseAdd',add_enable='^form.canWrite',
	                    del_action=None,del_class='buttonIcon icnBaseDelete',del_enable='^form.canWrite',
	                    close_action=None,close_class='buttonIcon icnTabClose',
	                    print_action=None,print_class='buttonIcon icnBasePrinter',
	                    pdf_action=None,pdf_class='buttonIcon icnBasePdf',pdf_name=None,
	                    export_action=None,export_class='buttonIcon icnBaseExport',
	                    tools_action=None,tools_class='buttonIcon icnBaseAction',tools_enable='^form.canWrite',tools_lbl=None,
	                    lock_action=False,tools_menu=None,upd_action=False,_onStart=False,
	                    filterOn=None,pickerPars=None,centerPaneCb=None,
	                    editorEnabled=None,parentLock='^status.locked',reloader=None,externalChanges=None,
	                    addOnCb=None,zoom=True,hasToolbar=False,
	                    canSort=True,
	                    **kwargs):









 MIEI APPUNTI

The components are situated in folders named "resources", or "_resources". In doesn't matter where these folders are, because the program
	search the component in every folder of the code.

	- includedViewBox
		The includedViewBox is a grid.

		Let's check out an example:

		es: 	bc = parentBC.borderContainer(**kwargs)
			pane = bc.contentPane(region='left',width='65%')
        		tc = bc.tabContainer(region='center')
			self.wounds_grid(tc.borderContainer(title='!!Wounds'))
			
			def wounds_grid(self,bc):
			    iv = self.includedViewBox(bc,
                                  add_action=True, # --> add the button "+", to add a new row
                                  del_action=True, # --> add the button "-", to delete a single row
                                  nodeId='WoundsGrid',
                                  editorEnabled=True,
                                  storepath='.wounds_base', # the path for data
                                  struct=self.ferite_struct,
                                  datamode='bag',label='!!Wounds')

			gridEditor = iv.gridEditor()
        		gridEditor.numberTextbox(gridcell='from') # --> name of grid columns
        		gridEditor.numberTextbox(gridcell='to')
        		gridEditor.numberTextbox(gridcell='value')

			def ferite_struct(self, struct):
        		    r = struct.view().rows()
        		    r.cell('da',name='Tiro da',dtype='L',width='3em')
        		    r.cell('a',name='Tiro a',dtype='L',width='3em')
        		    r.cell('valore',name='Valore',dtype='L',width='7em')

		Attention! The includedViewBox and its sons (for example, the selectionHandler) can accept only borderContainer
			and doesn't accept contentPane; in contentPane(s) you can't put other containers, you can only put objects