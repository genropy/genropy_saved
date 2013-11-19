# -*- coding: UTF-8 -*-

# bugsxml.py
# Created by Francesco Porcari on 2012-03-01.
# Copyright (c) 2012 Softwell. All rights reserved.

"Test page description"
from gnr.core.gnrdecorator import public_method

class GnrCustomWebPage(object):
    py_requires="gnrcomponents/testhandler:TestHandlerFull"


    def test_1_longtouch(self,pane):
        pane.data('.color','red')
        pane.div(height='100px',width='100px',margin='30px',background='^.color',id='red',display='inline-block',
                xconnect_touchstart="""
                                    SET .color="blue";
                                    genro._current_touch = {x:$1.pageX,
                                                            y:$1.pageY,start_time:new Date()};
                                    console.log('connect_touchstart',$1)
                                    """,
                xconnect_touchend="""SET .color="red";
                                    console.log('connect_touchend',$1);
                                    var startouch = genro._current_touch;
                                    genro._current_touch = null;
                                    var ct = $1.changedTouches?$1.changedTouches[0]:null;
                                    if(!ct){
                                        return;
                                    }
                                    var delta_x = ct.pageX - startouch.x;
                                    var delta_y = ct.pageY - startouch.y;
                                    var delta_time = new Date() - startouch.start_time;
                                    console.log('delta_x',delta_x,'delta_y',delta_y,'delta_time',delta_time)
                                    if(Math.abs(delta_y)<10 && Math.abs(delta_x)<10 && delta_time>500){
                                        alert('longtouch')
                                    }

                                    """)
        pane.div(height='100px',width='100px',margin='30px',background='green',id='green',display='inline-block')
