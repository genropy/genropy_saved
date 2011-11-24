# -*- coding: UTF-8 -*-
"""BorderContainer"""

class GnrCustomWebPage(object):
    py_requires = "gnrcomponents/testhandler:TestHandlerFull"
    
    def test_1_basic(self, pane):
        """Basic example"""
        bc = pane.borderContainer(height='400px')
        top = bc.contentPane(region='top', height='5em', background_color='#98C5EA')
        top.div('\"height\" attribute is mandatory on the \"top\" region',
                 margin='10px', text_align='center')
        center = bc.contentPane(region='center', background_color='#E1E9E9', padding='10px')
        center.div("""Like in Dojo, this widget is a container partitioned into up to five regions:
                   left (or leading), right (or trailing), top, and bottom with a mandatory center
                   to fill in any remaining space. Each edge region may have an optional splitter
                   user interface for manual resizing.""",
                   text_align='justify', margin='10px')
        center.div("""Sizes are specified for the edge regions in pixels or percentage using CSS – height
                   to top and bottom, width for the sides. You have to specify the "height" attribute
                   for the "top" and the "bottom" regions, and the "width" attribute for the "left" and
                   "right" regions. You shouldn’t set the size of the center pane, since it’s size is determined
                   from whatever is left over after placing the left/right/top/bottom panes.)""",
                   text_align='justify', margin='10px')
        left = bc.contentPane(region='left', width='130px', background_color='#FFF25D', splitter=True)
        left.div('\"width\" attribute is mandatory on the \"left\" region', margin='10px')
        right = bc.contentPane(region='right', width='15%', background_color='#FFF25D')
        right.div('\"width\" attribute is mandatory on the \"right\" region', margin='10px')
        bottom = bc.contentPane(region='bottom', height='20%', background_color='#98C5EA')
        bottom.div('\"height\" attribute is mandatory on the \"bottom\" region',
                    margin='10px', text_align='center')
                    
    def test_2_splitter(self, pane):
        """splitter example"""
        ta = 'center'
        m = '15px'
        bc = pane.borderContainer(height='400px')
        top = bc.contentPane(region='top',height='5em',splitter=True)
        top.div('I\'m top', text_align=ta, margin=m)
        left = bc.contentPane(region='left',width='20%',splitter=True)
        left.div('I\'m left', text_align=ta, margin=m)
        right = bc.contentPane(region='right',width='80px',splitter=True)
        right.div('I\'m right', text_align=ta, margin=m)
        bottom = bc.contentPane(region='bottom',height='80px',splitter=True)
        bottom.div('I\'m bottom', text_align=ta, margin=m)
        center = bc.contentPane(region='center',padding='10px')
        center.div('I\'m center (you cannot give me \"splitter\" attribute)', text_align=ta, margin=m)
        