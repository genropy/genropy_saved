.. _genro_hidden:

========
 hidden
========

    * :ref:`hidden_def`
    * :ref:`hidden_examples`

.. _hidden_def:

Definition
==========

    ::
    
        hidden = False

    If ``True``, allow to hide its object.

    **Validity:** it works on every object.

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