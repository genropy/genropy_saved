# -*- coding: UTF-8 -*-

"""Moveable"""

class GnrCustomWebPage(object):
    py_requires = "gnrcomponents/testhandler:TestHandlerFull"
    
    def isDeveloper(self):
        return True

    def test_1_basic(self, pane):
        """Basic test """
        box = pane.div(height='400px',width='400px',border='1px solid silver',margin='20px',#moveable_constrain=True,
                selfsubscribe_moveable_created="console.log('moveable_created',$1);",
                selfsubscribe_moveable_moved="console.log('moveable_moved',$1);")

        box.div(height='50px', width='100px', border='2px dotted red', 
                    background_color='yellow',
                    #top='30px',left='12px',
                    moveable=True ,lbl='Foo'
                    
                    )
        
        #pane.dataController("""console.log('moveable_created',$1)""",subscribe_moveable_created=True)
        #pane.dataController("""console.log('moveable_moved',$1)""",subscribe_moveable_moved=True)#