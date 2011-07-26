.. _action:

======
action
======
    
    *Last page update*: |today|
    
    * :ref:`action_def`
    * :ref:`action_validity`
    * :ref:`action_examples`
    
.. _action_def:

definition and description
==========================

    The *action* attribute is a javascript callback that receives all the ``**kwargs`` parameters.
    It receives a string with javascript code. For more information of the usage of javascript in
    Genro please check the :ref:`javascript` documentation section.
    
.. _action_validity:

validity
========
    
    The *action* attribute works on:
    
    * :ref:`button`
    * :ref:`checkboxcell`
    * :ref:`menu`
    
.. _action_examples:
    
examples
========
    
    **Example**:
    
    To create an alert message you have to write this line::
    
        pane.button('I\'m a button',action="alert('Hello!')")
        
    where ``'I\'m a button'`` is the label of the button.
    
    **Example**::
    
        class GnrCustomWebPage(object):
            def main(self,root,**kwargs):
                fb = root.formbuilder(cols=2)
                fb.div('The action attribute allow to write javascript code.',
                        font_size='.9em',text_align='justify',colspan=2)
                fb.button('Button',action="alert('Hello!')",tooltip='click me!')
                fb.div("""Create an alert message through "action" attribute.
                          There is a tooltip, too.""",
                        font_size='.9em',text_align='justify')
                fb.button('Format your system', action='confirm("Sure?")')
                fb.div('Create a confirm message through "action" attribute.',
                        font_size='.9em',text_align='justify')
                fb.button('Calculate Res', action="SET .res = screen.width+' x '+screen.height;")
                fb.textbox(lbl='res',value='^.res',width='6em')