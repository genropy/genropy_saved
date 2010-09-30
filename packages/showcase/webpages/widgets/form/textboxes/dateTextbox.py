# -*- coding: UTF-8 -*-

# dateTextbox.py
# Created by Niso on 2010-09-17.
# Copyright (c) 2010 Softwell. All rights reserved.

"""dateTextbox"""

class GnrCustomWebPage(object):
    py_requires="gnrcomponents/testhandler:TestHandlerFull"
    # dojo_theme='claro'    # !! Uncomment this row for Dojo_1.5 usage
    
    # For an exhaustive documentation, please see http://docs.genropy.org/widgets/form/textboxes/datetextbox.html
    
    #   - Other forms, attributes and items:
    #       In this section we report forms/attributes that have been used in this example
    #       despite they didn't strictly belonging to boxes.
    #       We also suggest you the file (if it has been created!) where you can find
    #       some documentation about them.
    #
    #       ## name ##          --> ## file ##
    #       cols                --> formbuilder.py
    #       datapath            --> datapath.py
    #       formbuilder         --> formbuilder.py
    #       value               --> datapath.py
    
    def test_1_dateTextbox(self,pane):
        """dateTextbox"""
        fb = pane.formbuilder(datapath='test1')
        fb.dateTextbox(value='^.dateTextbox',popup=True)
        