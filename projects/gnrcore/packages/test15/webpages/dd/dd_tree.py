# -*- coding: UTF-8 -*-

# dd_tree.py
# Created by Francesco Porcari on 2010-10-01.
# Copyright (c) 2010 Softwell. All rights reserved.

"""Tree with drag & drop"""

from gnr.core.gnrbag import Bag, DirectoryResolver

print 'Tree with drag & drop'
class GnrCustomWebPage(object):
    py_requires = """gnrcomponents/testhandler:TestHandlerFull"""

    def test_0_drop(self, pane):
        """Drop Boxes"""
        fb = pane.formbuilder(cols=1)
        dropboxes = fb.div(onDrop_text_plain='alert(data)',
                           onDrop_treenode="""console.log(data);alert(data.fullpath+' - '+data.relpath)""",
                           lbl='Drop boxes text/plain')

        dropboxes.div('no tags', width='100px', height='50px', margin='3px', background_color='lightgray',
                      float='left', dropTarget=True)
        dropboxes.div('only foo', width='100px', height='50px', margin='3px', background_color='#fcfca9',
                      float='left', dropTags='foo', dropTarget=True)
        dropboxes.div('only bar', width='100px', height='50px', margin='3px', background_color='#ffc2f5',
                      float='left', dropTags='bar', dropTarget=True)
        dropboxes.div('only foo AND bar', width='100px', height='50px', margin='3px', background_color='#a7cffb',
                      float='left', dropTags='foo AND bar', dropTarget=True)


    def test_1_simple(self, pane):
        """Simple Drag"""
        pane.css('.foo', 'color:pink;')
        pane.css('.bar', 'background-color:yellow;')
        root = pane.div(height='200px', overflow='auto')
        root.data('.tree.data', self.treedata())
        root.tree(storepath='.tree.data', dropTarget=True,
                  draggable=True,
                  onDrag="""function(dragValues){console.log(dragValues)}""",
                  dragClass='draggedItem',
                  onDrop_text_plain='alert(data)',
                  onDrop_treenode='alert(data.fullpath)')

    def test_2_disk(self, pane):
        """Disk Directory Drag"""
        root = pane.div(height='200px', overflow='auto')
        root.data('.disk', Bag(dict(root=DirectoryResolver('/Users/fporcari/Desktop'))))
        root.tree(storepath='.disk', hideValues=True, inspect='shift', draggable=True, dragClass='draggedItem')

    def test_3_data(self, pane):
        """Data Drag"""
        root = pane.div(height='200px', overflow='auto')
        root.tree(storepath='*D', hideValues=True, inspect='shift', draggable=True, dragClass='draggedItem')

    def test_4_source(self, pane):
        """Source Drag"""
        root = pane.div(height='200px', overflow='auto')
        root.tree(storepath='*S', hideValues=True, inspect='shift', draggable=True, dragClass='draggedItem')





        #fb=pane.formbuilder(cols=1,dragClass='draggedItem')
        #fb.div('Drag Me',width='70px',height='30px',margin='3px',
        #            background_color='green',lbl='drag it',draggable=True)
        #fb.data('.mydiv','aaaabbbbbccc',draggable=True)
        #fb.textBox(value='^.name',lbl='my name',draggable=True)
        #fb.div('^.mydiv',lbl='my div',draggable=True)
        #
        #fb.div('drag foo',dragTags='foo',lbl='drag with foo')
        #fb.div('drag bar',dragTags='bar',lbl='drag with bar')
        #fb.div('drag foo,bar',dragTags='foo,bar',lbl='drag with foo,bar')
        #


    def treedata(self):
        b = Bag()
        b.setItem('person', None, node_class='foo')
        b.setItem('person.name', 'John', job='superhero', node_class='bar')
        b.setItem('person.age', 22)
        b.setItem('person.sport.tennis', 'good')
        b.setItem('person.sport.footbal', 'poor')
        b.setItem('person.sport.golf', 'medium')
        b.setItem('pet.animal', 'Dog', race='Doberman')
        return b
