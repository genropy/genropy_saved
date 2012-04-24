#!/usr/bin/env python
# encoding: utf-8
"""html.py"""

class GnrCustomWebPage(object):
    def main(self, root, **kwargs):
        bc = root.borderContainer(region='center',datapath='main')
        self.top(bc.contentPane(region='top',height='100px',_class='pbl_roundedGroup',margin='5px',background_color='white'))
        bottom=bc.borderContainer(region='center')
        left = bottom.borderContainer(region='left',width='50%')
        right = bottom.borderContainer(region='center',width='50%')

    def top(self,pane):
        pane.div('HTML Basics and how we define them in python',_class='pbl_roundedGroupLabel')
        desc = """We should start with some simple familiar html elements and attributes such as div(), span() or table </BR>
                  If you understand html then you can understand that we are creating html from python.
                  For example, we can then show that a formbuilder in python, is just creating an html table in a fast way.

                  """
        pane.div(desc, margin='5px')