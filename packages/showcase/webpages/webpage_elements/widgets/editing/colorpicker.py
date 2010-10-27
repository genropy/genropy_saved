#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-

#  Created by Giovanni Porcari on 2007-03-24.
#  Copyright (c) 2007 Softwell. All rights reserved.

class GnrCustomWebPage(object):
    def main(self,root,**kwargs):
        center=root.borderContainer(region='center')
        center.data('aux.zoom',100)
        center.dataController("""
                        zoom = zoom || 100;
                        SET aux.zoom_factor= zoom+'%';
                        """,zoom='^aux.zoom', _onStart=True)
        bottomleft=center.contentPane(region='top',height=225,splitter=True)
        bottomleft.colorPicker(value='^aux.color',showHsv=False,showRgb=False,webSafe=False,showHex=False)
        bottomleft.horizontalSlider(lbl='!!Zoom',value='^aux.zoom',width='200px', 
                                         minimum=50,maximum=200,float='left',discreteValues=31)
        bottomleft.numberTextbox(value='^aux.zoom',places=0)
        square=center.contentPane(region='center').div(padding='20px',height='200px',width='200px',
                                                       background_color='^aux.color',zoomFactor='^aux.zoom_factor')
        square.div(height='200px',width='200px',border='1px solid black;').div('Testo')