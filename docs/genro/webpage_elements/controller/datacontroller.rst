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

	``dataController`` allows to execute a script without putting any values into any records.

	.. _datacontroller-syntax:

Syntax
======

	``object.datacontroller('action','shooter')``

	Where:

	- first parameter: here lies the code about the action that ``datacontroller`` has to do.

	- second parameter: here lies the "shooter", that is the way through wich the action is fired.

	.. _datacontroller-examples:

Examples
========

	In the following example you find a ``dataController`` in which the first parameter is a javascript action, while the second parameter is a folder path with a circumflex accent [#]_::
		
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

**Footnotes**:
	
.. [#] For further details on the circumflex accent, check :ref:`datastore-syntax`.
