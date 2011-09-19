.. _action:

======
action
======
    
    *Last page update*: |today|
    
    .. note:: **validity** - the *action* attribute is supported by:
              
              * :ref:`button`
              * :ref:`checkboxcell`
              * :ref:`menu`
              
    The *action* attribute allows to write javascript code [#]_.
    
    For example, if you use the *action* attribute on a button, the javascript
    code will be executed after user click the button
    
    **Example**:
    
        To create an alert message you have to write this line::
        
            pane.button('I\'m a button',action="alert('Hello!')")
            
        where ``'I\'m a button'`` is the label of the button.
        
    **Example**
    
        This is another example::
        
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
                    
**Footnotes**:

.. [#] For more information of the usage of javascript in Genro please check the :ref:`javascript` section.