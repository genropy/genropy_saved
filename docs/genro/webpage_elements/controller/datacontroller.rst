	.. _genro-datacontroller:

================
 dataController
================

	- :ref:`datacontroller-description`

	- :ref:`datacontroller-syntax`

	- :ref:`datacontroller-examples`

	.. _datacontroller-description:

Description
===========

	The ``dataController`` is just a javascript code that is executed when a parameter value changes.

	The ``dataController`` belongs to :ref:`genro-client-side-controllers` family.

	.. _datacontroller-syntax:

Syntax
======

	``object.dataController('action',shooter='^folderPlace','otherParams')``

	Where:

	- first parameter: here lies the code that ``datacontroller`` has to execute.

	- second parameter: here lies the "shooter", that is the way through wich the action is fired.
	
	- next parameters: here lie all the variables used in the 'action' (the first parameter): check for the following :ref:`datacontroller-examples` for further information.

	.. _datacontroller-examples:

Examples
========

	In the following example you find a ``dataController`` in which the first parameter is a javascript action, while the second parameter is a folder path with a circumflex accent [#]_.
	
	Example::
		
		class GnrCustomWebPage(object):
			def main(self,root,**kwargs):
				bc = root.borderContainer()
				top = bc.contentPane(region='top',height='100px')
				top.button('Build',fire='build')
    
				top.button('Add element',fire='add')
				top.dataController("""var pane = genro.nodeById('remoteContent')
				                      pane._('div',{height:'200px',width:'200px',background:'lightBlue',
				                                    border:'1px solid blue','float':'left',
				                                    remote:{'method':'test'}});
				                   """,_fired="^add")

				center = bc.contentPane(region = 'center').div(nodeId='remoteContent')
				center.div().remote('test',_fired='^build')

			def remote_test(self,pane,**kwargs):
			    print 'pippo'
			    pane.div('hello',height='40px',width='80px',background='lime')
	
	Example::
		
		class GnrCustomWebPage(object):
			def main(self,root,**kwargs):
				bc = pane.borderContainer(height='200px')
				
				bc.div('In this basic example we want to show you two equivalent syntax to write the dataController:',
				        font_size='.9em',text_align='justify')
				bc.div("""1) The first syntax is fb.dataController(\"SET .aaa=\'positive number\'\" ,_if='shooter>=0',
				             _else=\"SET .aaa=\'negative number\'\",shooter=\'^.x\') """,
				             font_size='.9em',text_align='justify')
				bc.div("""2) The second syntax is fb.dataController(\"\"\"if(shooter>=0){SET .bbb=\'positive number\';}
				             else{SET .bbb=\'negative number\';}\"\"\",shooter=\'^.y\');""",
				             font_size='.9em',text_align='justify')
				
				fb = bc.formbuilder(cols=3,datapath='test1')
				
				fb.dataController("SET .aaa='positive number'" ,_if='shooter>=0',
				                    _else="SET .aaa='negative number'",shooter='^.x')
				fb.div('1)',font_size='.9em',text_align='justify')
				fb.numberTextbox(value='^.x',lbl='x')
				fb.textbox(value='^.aaa',margin='10px',lbl='aaa')
				
				fb.dataController("""if(shooter>=0){SET .bbb='positive number';}
				                       else{SET .bbb='negative number';}""",
				                       shooter='^.y')
				fb.div('2)',font_size='.9em',text_align='justify')
				fb.numberTextbox(value='^.y',lbl='y')
				fb.textbox(value='^.bbb',margin='10px',lbl='bbb')

**Footnotes**:
	
.. [#] For further details on the circumflex accent, check :ref:`datastore-syntax`.
