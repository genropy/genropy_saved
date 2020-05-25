# -*- coding: utf-8 -*-

from gnr.core.gnrbag import Bag
from gnr.core.gnrdecorator import public_method

class GnrCustomWebPage(object):
    py_requires="gnrcomponents/testhandler:TestHandlerFull"

    def test_0_w3w(self,pane):
        bc = pane.borderContainer(height='600px',width='800px')
        top = bc.contentPane(region='top',padding='10px')
        fb = top.formbuilder()
        fb.geoCoderField(value='^.fulladdress',lbl='Full Address',country='IT',
                       selected_position='.geocoords',
                       selected_w3w='.w3w',
                       width='30em')
        fb.div('^.geocoords',lbl='Coords')
        fb.div('^.w3w.words',lbl='W3W')
        center = bc.contentPane(region='center')
        
        m = center.GoogleMap(height='100%', width='100%',
                    map_event_bounds_changed="""genro.w3w.drawGrid(this,$1)""",
                     map_type='satellite',
                     map_center='^.geocoords',
                     nodeId='gma',
                     w3w='.w3w',
                     centerMarker=dict(title='', label='X',draggable=True,
                                        event_dragend="genro.w3w.setCurrentW3W(this,$1);"),
                     autoFit=True)
        bc.dataFormula('.w3w',"genro.w3w.convertTo3wa(geocoords)",geocoords='^.geocoords')
        bc.dataController('sn.markers.center_marker.setTitle(w3w_words)',
                        w3w_words='^.w3w.words',sn=m,_delay=500)

