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

     
                
