# -*- coding: UTF-8 -*-
"""Stack container"""

class GnrCustomWebPage(object):
    py_requires = "gnrcomponents/testhandler:TestHandlerFull"
    
    def test_1_basic(self, pane):
        """Basic stackContainer"""
        bc = pane.borderContainer(height='300px')
        top = bc.contentPane(region='top') # height is given automatically through the slotToolbar
        sb = top.slotToolbar(slots='10,my_slot,*')
        sb.my_slot.filteringSelect(value='^.selectedPage',values='one:page one,two:page two,three:page three')
        center = bc.contentPane(region='center')
        sc = center.stackContainer(region='center', selectedPage='^.selectedPage')
        stack_one = sc.contentPane(background='#F0F1A5', pageName='one')
        stack_one.div('A div included in the first stack page',
                       margin='1em', display='inline-block',
                       border='3px solid gray', width='400px', height='100px',
                       rounded=5, font_size='1.3em', text_align='justify')
        stack_two = sc.contentPane(background='#ABDCEA', pageName='two')
        stack_two.div('A div included in the second stack page',
                       margin='2em', display='inline-block',
                       border='3px solid gray', width='400px', height='100px',
                       rounded=5, font_size='1.3em', text_align='justify')
        stack_three = sc.contentPane(background='#77C67C', pageName='three')
        stack_three.div('A div included in the third stack page',
                         margin='3em', display='inline-block',
                         border='3px solid gray', width='400px', height='100px',
                         rounded=5, font_size='1.3em', text_align='justify')