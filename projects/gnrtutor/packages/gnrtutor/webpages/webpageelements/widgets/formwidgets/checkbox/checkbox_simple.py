# -*- coding: UTF-8 -*-


"""Checkbox Examples"""

from tutorlib import example
class GnrCustomWebPage(object):
    py_requires = "examplehandler:ExampleHandlerFull"    
    
    @example(code='1',height=120,description='Simple checkbox')
    def checkbox(self, pane):
        pane.checkbox(value='^.my_value', label='My Check box')
        
        
    def doc_checkbox(self):
        """
"""

    @example(code='1',height=200,description='Ways to create check boxes')
    def checkbox2(self,pane):
        labels = 'First,Second,Third'
        labels = labels.split(',')
        pane = pane.formbuilder()
        for label in labels:
            pane.checkbox(value='^.%s_checkbox' % label, label=label)

    def doc_checkbox2(self):
        """This example show how multiple checkboxes can be created with a for loop
"""