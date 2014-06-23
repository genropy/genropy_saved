# -*- coding: UTF-8 -*-

# thermopane.py
# Created by Francesco Porcari on 2010-08-13.
# Copyright (c) 2011 Softwell. All rights reserved.

from gnr.web.gnrbaseclasses import BaseComponent

class ThermoPane(BaseComponent):
    """
    -Datastore:
        <title>mybatch</title>
        <items>
            <foo  max=100 message='client: James Brown' progress=40 />
            <bar  max=133 message='invoice: xyz100' progress=33 />
        </items>
        <status hidden=true>
        </status>
        
    -Parameters:    
    




    """

    def thermoFloating(self, pane):
        fp = pane.floatingPane(title='public floating', _class='shadow_4', nodeId='thermoFloating', datapath='_thermo',
                               top='80px', left='20px', width='400px', visible=False, dockTo='invisible_dock',
                               closable=False, resizable=True, resizeAxis='xy', maxable=False, dockable=True,
                               duration=400)
        pane.dock(nodeId='invisible_dock', hidden=True)

        fp.dataController("""
                            genro.dlg.
                            
                            genro.wdgById('thermoFloating').show();
                                """, _fired="^.show")


    def thermoPane(self, pane, nodeId=None, title=None, datapath=None, items=None):
        box = pane.div(datapath=datapath, hidden='^.status?hidden')
        for item in items.split(','):
            linemaker = getattr(self, 'thp_line_%s' % item, self.thp_makeline)
            line = box.div(datapath='.items.%s' % item, _class='thermoline')
            linemaker(line, item)

    def thp_makeline(self, pane, item):
        pane.div('^.?message', height='1em', text_align='center')
        pane.progressBar(width='25em', indeterminate='^.?indeterminate', maximum='^.?maximum', height='17px',
                         places='^.?places', progress='^.?progress', margin_left='auto', margin_right='auto')
