#!/usr/bin/env python
# encoding: utf-8
"""bag_intro.py"""

class GnrCustomWebPage(object):
    def main(self, root, **kwargs):
        bc = root.borderContainer(region='center',datapath='main')
        self.top(bc.contentPane(region='top',height='100px',_class='pbl_roundedGroup',margin='5px',background_color='white'))
        bottom=bc.borderContainer(region='center')
        left = bottom.borderContainer(region='left',width='50%')
        right = bottom.borderContainer(region='center',width='50%')

    def top(self,pane):
        pane.div('Bags Introduction',_class='pbl_roundedGroupLabel')
        desc = """Bags Intro discussion
                  """
        pane.div(desc, margin='5px')