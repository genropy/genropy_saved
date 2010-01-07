#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#
#  untitled
#
#  Created by Giovanni Porcari on 2007-03-24.
#  Copyright (c) 2007 Softwell. All rights reserved.
#

""" staff """
import os

from gnr.core.gnrbag import Bag,GeoCoderBag
from gnr.core.gnrstring import templateReplace, splitAndStrip

class GnrCustomWebPage(object):
    py_requires='basecomponent:Public'
    def windowTitle(self):
         return '!!Assopy Mappa Pythonisti'
         
    def htmlHeaders(self):
        googlekey='ABQIAAAAUwVfREP6FPJzAIxWuaT4_BQXq7bWTC04Ff1KKaIsErBhwE7B5xSKrucRzm000Ur7Cm-a9MmuppH4ag'
        self.addHtmlHeader('script',src="http://maps.google.com/maps?file=api&amp;v=2&amp;key=%s"%googlekey,type="text/javascript")
        self.addHtmlHeader('script',src="http://gmaps-utility-library.googlecode.com/svn/trunk/markermanager/release/src/markermanager.js",type="text/javascript")

    def pageAuthTags(self, method=None, **kwargs):
        return 'superadmin'
        
    def main(self, root, **kwargs):
        root.dataRpc('current.location','getLocation',pkey='^current.user_id')
        root.dataScript('dummy','var node=genro.nodeById("mappa");var loc=node.getMapLoc(coordinates);node.googleMap.panTo(loc)',
                                                        coordinates='^current.location.coordinates')
        
        root.dataScript('dummy',"""var node=genro.nodeById("mappa");
                                   var marker=node.newMarker(coordinates);
                                   node.googleMap.addOverlay(marker)""",
                                   coordinates='=current.location.coordinates',_fired='^setMarker')
        lc,top = self.publicRoot(root)
        top.div('!!Mappa Pythonisti')
        top=lc.contentPane(layoutAlign='top',height='34px',border_left='1px solid silver',
                                                               border_right='1px solid silver')
        fb=top.formbuilder(margin_left='10px',cols=4,border_spacing='2px')
        
        fb.dbSelect(lbl='Cerca', value = '^current.user_id',ignoreCase=True,dbtable='assopy.utente',columns='nome_cognome')
        fb.button('Set Marker',fire='setMarker')    
        tc = lc.contentPane(layoutAlign='client',border='1px solid silver')
        tc.googleMap(nodeId='mappa',width='750px',height='384px',margin='3px',
                     map_controls='LargeMap,Scale,MapType',overflow='hidden',border='1px solid silver')
                     
    def rpc_getLocation(self,pkey):
        s=self.db.table('assopy.utente').query(columns='@assopy_anagrafica_utente_id.geolocator as geoloc',
                    where='$id=:pkey',pkey=pkey).selection().output('dictlist')
        if s:
            locator=GeoCoderBag()
            locator.setGeocode('curr',s[0]['geoloc'])
        return locator['curr']
        

