.. _genro_hidden:

========
 hidden
========

	* :ref:`hidden_def`
	* :ref:`hidden_validity`
	* :ref:`hidden_examples`

.. _hidden_def:

Definition
==========

	If ``True``, allow to hide its object.
	
.. _hidden_validity:

Validity and default value
==========================

	**Validity:** the ``hidden`` attribute works on every object.

	**default value:** the default value of ``hidden`` is ``False``::

		hidden = False

.. _hidden_examples:

Examples
========

	::

		class GnrCustomWebPage(object):
			def main(self,root,**kwargs):
				bc = root.borderContainer(height='100px',datapath='test4')
				bc.data('.hidden',False,_init=True)
				bc.dataController("""SET .hidden=true""",_fired='^.invisibility')
				bc.dataController("""SET .hidden=false""",_fired='^.show')
				fb = bc.formbuilder(cols=2)
				fb.button('Hide the div!',fire='^.invisibility')
				fb.button('Show the div!',fire='^.show')
				fb.div('You can hide me!',hidden='^.hidden',colspan=2,border='4px solid red')