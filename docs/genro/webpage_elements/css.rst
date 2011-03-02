.. _genro_css:

============
CSS elements
============

    Cascading Style Sheets (CSS [#]_) is a way to turn your ugly pages into something beautiful. More properly, CSS is a simple mechanism for adding style (e.g., fonts, colors, spacing) to Web documents.

    .. note:: The only difference with standard CSS lies in the syntax: you have to use the "_" symbol in place of the "-" symbol.

CSS examples
============
    
    Here we show a simple example::
    
        #!/usr/bin/env pythonw
        # -*- coding: UTF-8 -*-
        
        import datetime
        
        class GnrCustomWebPage(object):
            def main(self, root, **kwargs):
                root.div('Hello!',font_size='40pt',border='3px solid yellow', padding='20px')
                
                root.data('demo.today',datetime.date.today())
                root.dateTextBox(value='^demo.today')
                
                root.div('^demo.today', font_size='20pt', border='3px solid yellow', 
                          padding='20px', margin_top='5px', format='long')
                          
    So:
        
        +----------------------+-----------------------+
        | normal webpage style |      Genro style      |
        +======================+=======================+
        |   font-size='40pt'   |    font_size='40pt'   |
        +----------------------+-----------------------+
        |   margin-top='40pt'  |   margin_top='40pt'   |
        +----------------------+-----------------------+
        
**Footnotes**:

.. [#] For all the informations about CSS, please check the CSS_ site.

.. _CSS: http://www.w3.org/Style/CSS/