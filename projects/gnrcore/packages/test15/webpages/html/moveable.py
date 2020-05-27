# -*- coding: utf-8 -*-

"""Moveable"""

class GnrCustomWebPage(object):
    py_requires = "gnrcomponents/testhandler:TestHandlerFull"
    dojo_source=True

    def isDeveloper(self):
        return True

    def test_1_basic(self, pane):
        """Basic test """
        box = pane.div(height='400px',width='400px',border='1px solid silver',position='relative',
               datapath='blackboard',#resize='both',overflow='auto',
                selfsubscribe_onMoveable="console.log('moveable',$1.action,$1.sourceNode,$1.top,$1.left);")
        
        for n in range(1):
            box.div(height='50px', width='100px', background_color='yellow',position='absolute',top='%ipx'%(20+n*10),
                left='%ipx'%(20+n*10),
                moveable=True ,resize='both', overflow='auto',

                lbl='Object %s' %n)
        
        #pane.dataController("""console.log('moveable_created',$1)""",subscribe_moveable_created=True)
        #pane.dataController("""console.log('moveable_moved',$1)""",subscribe_moveable_moved=True)#