# -*- coding: UTF-8 -*-
# 
"""ClientPage tester"""

class GnrCustomWebPage(object):
    py_requires = "gnrcomponents/testhandler:TestHandlerFull,"
   
    
    def test_1_plain(self, pane):
        """Set in external store"""
       # m=pane.div(height='200px',width='200px',border='1px solid silver',rounded=10)
        pane.data('.center','Via omboni 10 abbiategrasso')
        pane.data('.zoom',10)
        pane.data('.maptype','roadmap')
        bc=pane.borderContainer(height='600px')
        top=bc.contentPane(region='top')
        fb=top.formbuilder(cols=3)
        fb.geoCoderField(value='^.center',lbl='Center',selected_position='.center_position')
        fb.div(innerHTML='^.center_position',lbl='center position')
        fb.FilteringSelect(value='^.maptype',lbl='Map Type',values='roadmap:Roadmap,hibrid:Hibryd,satellite:Satellite,terrain:Terrain')
        fb.textbox(value='^.marker_name',lbl='Marker name')
        fb.geoCoderField(value='^.marker_address',lbl='marker',selected_position='.marker')
        fb.div(innerHTML='^.marker',lbl='marker position')
        fb.horizontalSlider(value='^.zoom',lbl='Zoom',minimum=4,maximum=21,width='150px',discreteValues=18)

        c=bc.contentPane(region='center',dropTarget=True,onDrop="""console.log(dropInfo);
                                     for (var k in data){
                                         alert(k+' :'+data[k])
                                         }""",dropTypes='*')
        m=c.GoogleMap(height='100%',border='1px solid silver',rounded=10,
                     map_center="^.center",map_type='^.maptype',
                     map_zoom='^.zoom',map_disableDefaultUI=True,connect_onclick='function(e){alert("click")}')
        
        fb.dataController("""if (marker_name){
        console.log('MARKER',marker)
                                 kw={title:marker_name,draggable:true}
                                 mapNode.gnr.setMarker(mapNode,marker_name,marker,kw)
                           }
                           """,marker='^.marker',marker_name='=.marker_name',mapNode=m)
    
    def test_2_palette(self,pane):
        pane.data('.center','Via omboni 10 abbiategrasso')
        pane.data('.zoom',10)
        pane.data('.maptype','roadmap')
        bc=pane.borderContainer(height='600px')
        top=bc.contentPane(region='top')
        fb=top.formbuilder(cols=3)
        fb.geoCoderField(value='^centertest',lbl='Center',selected_position='.center_position')
        fb.div(innerHTML='^.center_position',lbl='center position')
        fb.FilteringSelect(value='^maptypetest',lbl='Map Type',values='roadmap:Roadmap,hibrid:Hibryd,satellite:Satellite,terrain:Terrain')
        fb.textbox(value='^.marker_name',lbl='Marker name')
        fb.geoCoderField(value='^.marker_address',lbl='marker',selected_position='.marker')
        fb.div(innerHTML='^.marker',lbl='marker position')
        fb.horizontalSlider(value='^zoomtest',lbl='Zoom',minimum=4,maximum=21,width='150px',discreteValues=18)

        pane.paletteMap(paletteCode='map',dockTo=False,map_center="^centertest",map_type='^maptypetest',
                     map_zoom='^zoomtest',map_disableDefaultUI=True)
    
    
    def test_3_paletteDynamic(self,pane):
        pane.data('.center','Via omboni 10 abbiategrasso')
        pane.data('.zoom',10)
        pane.data('.maptype','roadmap')
        bc=pane.borderContainer(height='600px')
        top=bc.contentPane(region='top')
        fb=top.formbuilder(cols=3)
        fb.geoCoderField(value='^.center',lbl='Center',selected_position='.center_position')
        fb.div(innerHTML='^.center_position',lbl='center position')
        fb.FilteringSelect(value='^.maptype',lbl='Map Type',values='roadmap:Roadmap,hibrid:Hibryd,satellite:Satellite,terrain:Terrain')
        fb.textbox(value='^.marker_name',lbl='Marker name')
        fb.geoCoderField(value='^.marker_address',lbl='marker',selected_position='.marker')
        fb.div(innerHTML='^.marker',lbl='marker position')
        fb.horizontalSlider(value='^.zoom',lbl='Zoom',minimum=4,maximum=21,width='150px',discreteValues=18)
        fb.button('Make Palette',action='genro.dlg.paletteMap({map_center:center,map_type:maptype,map_zoom:zoom});',
                  center='=.center',maptype='=.maptype',zoom='=.map_zoom')

    def test_4_staticMap(self,pane):
        pane.data('.center','Via omboni 10 abbiategrasso')
        pane.data('.zoom',10)
        pane.data('.maptype','roadmap')
        bc=pane.borderContainer(height='600px')
        top=bc.contentPane(region='top')
        fb=top.formbuilder(cols=3)
        fb.geoCoderField(value='^.center',lbl='Center',selected_position='.center_position')
        fb.div(innerHTML='^.center_position',lbl='center position')
        fb.FilteringSelect(value='^.maptype',lbl='Map Type',values='roadmap:Roadmap,hibrid:Hibryd,satellite:Satellite,terrain:Terrain')
        fb.textbox(value='^.marker_name',lbl='Marker name')
        fb.geoCoderField(value='^.marker_address',lbl='marker',selected_position='.marker')
        fb.div(innerHTML='^.marker',lbl='marker position')
        fb.horizontalSlider(value='^.zoom',lbl='Zoom',minimum=4,maximum=21,width='150px',discreteValues=18)
        fb.staticMap(map_center='^.center',map_maptype='^.maptype',map_zoom='^.zoom',height='200px',width='400px',
                    marker_p='Via cesare battisti 3, abbiategrasso',
                    centerMarker=True)
        
        #fb.button('Make Palette',action='genro.dlg.paletteMap({map_center:center,map_type:maptype,map_zoom:zoom});',
        #          center='=.center',maptype='=.maptype',zoom='=.map_zoom')
        #
                
    def test_5_staticmap_simple(self,pane):
        fb = pane.formbuilder(cols=2, border_spacing='3px')
        fb.geoCoderField(value='^.addr',lbl='Addr',selected_position='.addr_position')
        fb.textbox(value='^.addr_position')
        fb.staticMap(map_center='^.addr',centerMarker=True,height='150px',width='200px')
        fb.staticMap(map_center='^.addr_position',centerMarker=True,height='150px',width='200px')

    def test_6_dynamicmap_simple(self,pane):
        fb = pane.formbuilder(cols=2, border_spacing='3px')
       # fb.data('.addr','via omboni 10 abbiategrasso')
        fb.geoCoderField(value='^.addr',lbl='Addr',selected_position='.addr_position')
        fb.GoogleMap(map_center='^.addr',centerMarker=True,height='150px',width='200px')


