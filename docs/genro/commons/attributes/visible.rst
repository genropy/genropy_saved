.. _visible:

=======
visible
=======
    
    *Last page update*: |today|
    
    .. note:: **validity** - the *hidden* attribute is supported by every :ref:`webpage element
              <we>`
    
    * :ref:`visible_def`
    * :ref:`visible_examples`
    
.. _visible_def:

description
===========
    
    Boolean. If ``True``, make visible an object. If ``False``, hide the boxes but keep
    the boxes content. Also, the physical space occupied from the object in the webpage
    is kept (empty).
    
.. _visible_examples:

examples
========

    Let's see an example with the differences between the :ref:`hidden` and the :ref:`visible`
    attribute::
    
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
                                    hidden='^.hidden',visible='^.visible')
                fb.textbox(value='^.name', lbl='Name')
                fb.textbox(value='^.surname', lbl='Surname')
                fb.numberTextbox(value='^.age', lbl="Age")
                fb.dateTextbox(value='^.birthdate', lbl='Birthdate')
                fb.filteringSelect(value='^.sex', values='M:Male,F:Female', lbl='Sex')
                fb.textbox(value='^.job.profession', lbl='Job')
                fb.textbox(value='^.job.company_name', lbl='Company name')