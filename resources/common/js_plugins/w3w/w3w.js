var genro_plugin_w3w = {
    init:function(api_key){
        console.log('init w3w')
        this.api_key = api_key ||  genro._('gnr.api_keys.w3w?key');
        genro.dom.loadJs(`https://assets.what3words.com/sdk/v3/what3words.js?key=${this.api_key}`,
                        function(){
                            genro.w3w.api = what3words.api;
                            genro.w3w.client = what3words;
                        });
    },

    convertTo3wa:function(geocoords){
        if (!geocoords){
            return;
        }
        let c = geocoords.split(',');
        return genro.w3w.api.convertTo3wa({lat:c[0],lng:c[1]},genro.locale().split('-')[0]).then(function(w3wjson){
            return new gnr.GnrBag(w3wjson);
        });
    },


    setCurrentW3W:function(sourceNode,event){
        sourceNode.setAttributeInDatasource('w3w',genro.w3w.convertTo3wa(`${event.latLng.lat()},${event.latLng.lng()}`));
    },

    drawGrid:function(sourceNode,event){
        var map = sourceNode.map;

        const zoom = map.getZoom();
        const loadFeatures = zoom > 17;

        if (loadFeatures) { // Zoom level is high enough
        var ne = map.getBounds().getNorthEast();
        var sw = map.getBounds().getSouthWest();

        // Call the what3words Grid API to obtain the grid squares within the current visble bounding box
        what3words.api
            .gridSectionGeoJson({
                southwest: {
                    lat: sw.lat(), lng: sw.lng()
                },
                northeast: {
                    lat: ne.lat(), lng: ne.lng()
                }
                }).then(function(data) {
                if (sourceNode._gridData !== undefined) {
                    for (var i = 0; i < sourceNode._gridData.length; i++) {
                        map.data.remove(sourceNode._gridData[i]);
                    }
                }
                sourceNode._gridData = map.data.addGeoJson(data);
            }).catch(console.error);
        }

        // Set the grid display style
        map.data.setStyle({
            visible: loadFeatures,
            strokeColor: '#777',
            strokeWeight: 0.5,
            clickable: true,
            cursor:'pointer',
            });
    }
};


