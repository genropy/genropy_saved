.. _genro_css:

============
CSS elements
============

    CSS is a simple mechanism for adding style (e.g., fonts, colors, spacing) to Web documents.

    Keep in mind these two features when you use CSS on a Genro :ref:`genro_structure_mainproject`:
    
    * The only difference with standard CSS lies in the syntax: you have to use the "_" symbol in place of the "-" symbol::
    
        <!-- normal CSS style -->
        font-size='40pt'
        margin-top='40px'
        
        <!-- Genro CSS style  -->
        font_size='40pt'
        margin_top='40px'
        
    * You can import css files in your :ref:`genro_structure_mainproject` through the *css_requires* variable: check the :ref:`webpages_css_requires` section for further details.
    
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