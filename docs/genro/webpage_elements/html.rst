.. _html:

=============
HTML elements
=============
    
    *Last page update*: |today|
    
    You can use an HTML element following the device of the Genro HTML syntax: in Genro, every HTML element
    is defined as a Python function, like::
    
        <!-- HTML code: -->
        <div>I like Genropy!</div>
        
        # Genro code:
        div('I like Genropy!')
    
    Obviously, you have to give a kinship to every element of your code; let's see in the following example
    how kinship works in Genro:
    
    **HTML code**::
    
        <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
        <html>
            <head>
                <!-- Here lies the head stuff... -->
            </head>
            
            <body>
                <div style='height:400px'>
                    <div>I like Genropy!</div>
                </div>
            </body>
        </html>
        
    **Genro code**::
        
        def main(self,root,**kwargs):
            bc = root.borderContainer(height='400px')
            bc.div('I like Genropy!')
            
    As you can see in ``bc.div('I like Genropy!')``, Genro syntax use the point (``.``) to specify the kinship;
    you can append more than one son at a time to your father. In the following example, ``pane`` is the son of
    a ``borderContainer``, ``div`` is ``pane``'s son and ``IncludedView`` is ``div``'s son::
    
        pane.div(width='100%',height='300px').IncludedView(struct=self._gridStruct2(),
                                                           storepath='lista_regioni',nodeId='regioni_grid')
                                                           
    .. _html_elements:
    
list of HTML elements
---------------------

    Here we list the HTML elements:
    
    * *ghost*: the ghost attribute is deprecated. Use HTML placeholder instead.
    * *placeholder*: the html 5 placeholder
    * *tip*: the HTML tip, where STRING is the tip that will be showned.
      You can use it on every object.
    * *type*: allow to hide the written characters.