# -*- coding: UTF-8 -*-

# field.py
# Created by Filippo Astolfi on 2010-09-15.
# Copyright (c) 2010 Softwell. All rights reserved.

"""Field"""

from gnr.core.gnrbag import Bag

class GnrCustomWebPage(object):
    py_requires = "gnrcomponents/testhandler:TestHandlerFull"
    # dojo_theme='claro'    # !! Uncomment this row for Dojo_1.5 usage
    maintable = 'showcase.cast'

    def test_1_basic(self, pane):
        """Basic field"""
        pane.div("""In this basic test you see a simple field.""",
                    font_size='.9em', text_align='justify')
        pane.div("""1) Search for file model from which field draws going "in showcase/model/cast.py",
                    and search for the column labeled as "person_id".""",
                    font_size='.9em', text_align='justify')
        pane.div("""2) It looks like there is a "lbl" attribute, but if you see in the code you won't find it.
                    That's because if "lbl" is not defined, then field takes the label directly from file model.""",
                    font_size='.9em', text_align='justify')
        fb = pane.formbuilder(datapath='test2', cols=2)
        fb.field(field='person_id', rowcaption='$name')
        pane.div("""Field is a magic tool, because it takes the type you want and convert itself in the correct
                    widget to handle the data. For making "field" magic, you have to specify your data in the first
                    parameter, called "field". In this example, we put a table's ID.""",
                    font_size='.9em', text_align='justify')
        pane.div("""In place of 'showcase.cast.person_id' you could wrote 'person_id' adding in the file
                    requirments the following line: "maintable='showcase.cast'". So it's your choice to specify the main
                    table at the beginning of the code, or to specify it in the sintax of field ("showcase.cast").""",
                    font_size='.9em', text_align='justify')