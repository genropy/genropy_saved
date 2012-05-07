# -*- coding: UTF-8 -*-
"""simpleTextarea"""

from tutorlib import example

class GnrCustomWebPage(object):
    py_requires = "examplehandler:ExampleHandlerFull"


    @example(code=1,height=350,description='simpleTextarea')
    def simpleTextarea(self, pane):        
        pane.simpleTextarea(value='^.simpletextarea', height='80px', width='30em',
                            color='#605661', font_size='1.2em',
                            default='A simple area to contain text')

    def doc_simpleTextarea(self,pane):
        """A simple text area is a the widget to use when you have text that is more than one line.
You can set the height of the area, width, color and font_size and other html attributes.
"""