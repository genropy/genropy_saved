# -*- coding: UTF-8 -*-

"""Moveable"""

class GnrCustomWebPage(object):
    py_requires = "gnrcomponents/testhandler:TestHandlerFull"
    
    def isDeveloper(self):
        return True

    def test_1_basic(self, pane):
        """Basic test """
        pane.attributes.update(height='500px')
        pane.div(height='50px', width='100px', border='2px dotted red', background_color='yellow',moveable=True,lbl='Foo')
        
        pane.dataController("""console.log('moveable_created',$1)""",subscribe_moveable_created=True)
        pane.dataController("""console.log('moveable_moved',$1)""",subscribe_moveable_moved=True)