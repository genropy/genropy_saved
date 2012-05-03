# -*- coding: UTF-8 -*-


"""Checkbox Examples"""

from tutorlib import example
class GnrCustomWebPage(object):
    py_requires = "examplehandler:ExampleHandlerFull"    
    
    @example(code=1,height=120,description='Simple checkbox')
    def checkbox(self, pane):
        pane.checkbox(value='^.my_value', label='My Check box')
        
        
    def doc_checkbox(self):
        """
"""

    @example(code=2,height=200,description='Ways to create check boxes')
    def checkbox2(self,pane):
        labels = 'First,Second,Third'
        labels = labels.split(',')
        pane = pane.formbuilder()
        for label in labels:
            pane.checkbox(value='^.%s_checkbox' % label, label=label)

    def doc_checkbox2(self):
        """This example show how multiple checkboxes can be created with a for loop
"""
    @example(code=3,height=130,description='Maxi checkbox')
    def checkbox_maximized(self, pane):
        pane.checkbox(value='^.my_value', label='My Check box maximus')
        
        
    def doc_checkbox_maximized(self):
        """
        hqwgekdfgqskjdhfgakjhsdgfjasdgfkj
"""


#     @example(code=3,height=370,description='Datastore Inspector for above examples')
#     def dataStoreview(self,pane):
#         pane.div().img(src="http://content.screencast.com/users/jeff.edwards/folders/Jing/media/f416a9dc-19f0-4b33-8726-cc538e36d3ac/00000111.png")
#     
#     def doc_dataStoreview(self):
#         """If you have the developer privileges (developer tag), then you can invoke the datastore inspector by using control+shift+d
#         
# This will show you a representation of the datastore hierarchical bag in a tree.  You can see the paths to the values in the inspector.
# This example shows how to display an image in a div, by calling the img attribute. 
# """