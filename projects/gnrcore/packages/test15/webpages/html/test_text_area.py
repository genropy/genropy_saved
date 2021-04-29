# -*- coding: utf-8 -*-

"""Html elements tester"""

from builtins import range
from builtins import object

class GnrCustomWebPage(object):
    py_requires = "gnrcomponents/testhandler:TestHandlerBase"
    
    def test_0_textarea(self, pane):
        """Test Text area with connect_onkeyup to show available characters"""
        box = pane.div()
        box.textarea(value='^.text_msg', connect_onkeyup="""var tgt = $1.target
                                                        var my_text = tgt.value
                                                        var remaining = 30 - my_text.length
                                                        SET .rem = remaining
                                                        SET .clr = (remaining<10)?'red':'grey'
                                                        console.log(tgt)
                                                        if(remaining<3){
                                                            genro.playSound('ping')
                                                        }
                                                        if(remaining<0){
                                                            tgt.value = my_text.slice(0,30)
                                                        }
                                                        """)
        last_line = box.div(font_style='italic', font_size='8pt')
        last_line.span('Remaining: ')
        last_line.span('^.rem', color='^.clr')