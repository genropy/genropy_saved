.. _hidden:

======
hidden
======
    
    *Last page update*: |today|
    
    .. note:: **validity** - the *hidden* attribute is supported by every :ref:`webpage element
              <webpage_elements_index>`
    
    * :ref:`hidden_def`
    * :ref:`hidden_examples`
    
.. _hidden_def:

description
===========

    Boolean. If ``True``, allow to hide the webpage element to which it belongs.
    The physical space occupied from the object in the page is freed
    
.. _hidden_examples:

examples
========

    **A simple example**::
    
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
    
    **Differences between "hidden" and "visible"**::
    
        class GnrCustomWebPage(object):
            def test_4_test(self, pane):
                """hidden and visible"""
                bc = pane.borderContainer(datapath='test5')
                bc.data('^.visible',True)
                bc.div("""In this test you can see the effect of the three attributes
                          applied on the formbuilder:""",font_size='.9em', text_align='justify')
                bc.div("hidden: if True, the formbuilder is hidden",font_size='.9em', text_align='justify')
                bc.div("visible: if False, user can't see the formbuilder and its form fields",
                        font_size='.9em', text_align='justify')
                fb = bc.formbuilder(cols=2, fld_width='100%', width='100%')
                fb.checkbox(value='^.hidden', label='Hidden form')
                fb.checkbox(value='^.visible', label='Visible form')
                
                fb = bc.formbuilder(cols=3,fld_width='100%',width='100%',
                                    hidden='^.hidden', visible='^.visible')
                fb.textbox(value='^.name', lbl='Name')
                fb.textbox(value='^.surname', lbl='Surname')
                fb.numberTextbox(value='^.age', lbl="Age")
                fb.dateTextbox(value='^.birthdate', lbl='Birthdate')
                fb.filteringSelect(value='^.sex', values='M:Male,F:Female', lbl='Sex')
                fb.textbox(value='^.job.profession', lbl='Job')
                fb.textbox(value='^.job.company_name', lbl='Company name')