	.. _genro-data:

======
 data
======

	- :ref:`data-description`

	- :ref:`data-syntax`

	- :ref:`data-examples`

	.. _data-description:

Description
===========

	The ``data`` is a server-side Genro object that allows to define variables from server to client.

	.. _data-syntax:

Syntax
======

	``object``.data('folderPath','value')

	Where:

	- first parameter: it contains the variable folder path.

	- second parameter: it contains the value of the variable.

	.. _data-examples:

Examples
========

	Example::
	
		class GnrCustomWebPage(object):
			def main(self,root,**kwargs):
				root.data('icon','icnBaseOk')
				root.data('fontType','Courier')
				root.data('widthButton','10em')
				root.data('fontSize','22px')
				root.data('color','green')
				bc = root.borderContainer()
				bc.button('Click me',iconClass='^icon',width='^widthButton',color='^color',
				           font_size='^fontSize',font_family='^fontType',action="alert('Clicked!')")
	
	Example::
		
		def test_2_basic2(self,pane):
			"""data basic example - formbuilder attributes"""
			bc = pane.borderContainer(datapath='test2')
			fb = bc.formbuilder(cols=2)
			fb.data('.name','Filippo')
			fb.data('.surname','Astolfi')
			fb.textbox(value='^.name',lbl='!!Name')
			fb.textbox(value='^.surname',lbl='!!Surname')
			fb.numberTextbox(value='^.phone',lbl='!!Phone number')
			fb.textbox(value='^.address',lbl='!!Address')
			