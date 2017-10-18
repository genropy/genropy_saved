# -*- coding: UTF-8 -*-

"""Html iframe tester"""

class GnrCustomWebPage(object):
    py_requires = "gnrcomponents/testhandler:TestHandlerBase"
    
    
    def test_1_basic(self, pane):
        """Basic test for a div with no attributes"""
        bc = pane.borderContainer(height='800px',width='800px')
        center = bc.contentPane(region='center',overflow='hidden')
        center.htmliframe(src='http://mappe.comune.genova.it/mapstore/?public=yes&mapId=805',height='100%',width='100%',border='0px')

