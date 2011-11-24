#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-

#  Created by Giovanni Porcari on 2007-03-24.
#  Copyright (c) 2007 Softwell. All rights reserved.

class GnrCustomWebPage(object):
    def main(self, root, **kwargs):
        rootbc = root.borderContainer(border='6px solid navy', margin='10px', background_color='red')
        rootbc.contentPane(region='top', height='50px', background_color='silver').div('io sono il super top')
        mainbc = rootbc.borderContainer(region='center', border='3px solid red', margin='10px',
                                        background_color='white')
        mainbc.contentPane(region='top', height='30px', splitter=True, background_color='pink').div('io sono il top')
        mainbc.contentPane(region='bottom', height='30px', splitter=True, background_color='yellow').div(
                'io sono il bottom')
        mainbc.contentPane(region='right', width='100px', splitter=True, background_color='orange').div(
                'io sono destra')
        center = mainbc.tabcontainer(region='center', datapath='rightdata')
        for k in range(9):
            self.oneColumn(center.contentPane(title='tab %i' % k, datapath='dati_%i' % k))

    def oneColumn(self, bc):
        top = bc.contentPane(region='top', splitter=True)
        center = bc.contentPane(region='center')
        self.mydata(bc) # inizializzo dati
        self.mycontroller(bc) # definisco formule
        self.topPane(top) # creo il top
        self.centerPane(center) #creo il center

    def mydata(self, pane):
        pane.data('.width', 200)
        pane.data('.bordo', '1px solid green')

    def mycontroller(self, pane):
        pane.dataFormula('.height', 'mywidth/2', mywidth='^.width', _onStart=True)
        pane.dataFormula('.width_px', 'mywidth+"px"', mywidth='^.width', _onStart=True)
        pane.dataFormula('.height_px', 'myheight+"px"', myheight='^.height')

    def topPane(self, pane):
        fb = pane.formbuilder(cols=1)
        fb.horizontalSlider(lbl='!!Larghezza', value='^.width', width='200px',
                            minimum=0, maximum=1000, intermediateChanges=True)
        fb.horizontalSlider(lbl='!!Altezza', value='^.height', width='200px',
                            minimum=0, maximum=1000, intermediateChanges=True)

    def centerPane(self, pane):
        quadro = pane.div(height='^.height_px', width='^.width_px',
                          background_color='yellow', border='^.bordo')
        for k in range(100):
            quadro.div('%i' % k, height='10px', width='10px', font_size='7px', border='1px solid red', margin='3px',
                       float='left')