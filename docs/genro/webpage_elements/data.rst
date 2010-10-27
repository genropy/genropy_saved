	.. _genro-data:

======
 data
======

	The 
	il data, non fa partire script, mette solamente un qualcosa in un qualche posto

	il data è serverside

	??? write of "pane.data('numero','2')"

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