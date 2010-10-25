	.. _genro-dataformula:

=============
 dataformula
=============

	``dataformula`` allows to insert a value into a specific address of the :ref:`genro-datastore`.

	**Syntax**:
	
		``First parameter: folderPlaceOfYourValue;``

		``second parameter: formula;``
		
		``next parameters: variables;``

	Example::
	
		root.dataFormula('somma','a+b',a='^a',b='1')
	
	Example::

		class GnrCustomWebPage(object):
			def main(self,root,**kwargs):
				fb = root.formbuilder(cols=2)
				fb.horizontalSlider(lbl='Base',value='^base',width='200px',minimum=1,maximum=100)
				fb.numberTextBox(value='^base',places=2)
				fb.horizontalSlider(lbl='Height',value='^height',width='200px',minimum=1,maximum=100)
				fb.numberTextBox(value='^height',places=2)
				fb.dataFormula('area','base * height', base='^base', height='^height')
				fb.numberTextBox(lbl='!!Area',value='^area',places=2,border='2px solid grey',padding='2px')