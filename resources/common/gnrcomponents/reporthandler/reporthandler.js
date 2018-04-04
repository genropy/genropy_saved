dojo.declare("gnr.widgets._reportHandlerLayout", gnr.widgets.UserObjectLayout, {
    objtype:'rh_conf',
    newcaption:'New',
    default_configurator_pars:{palette:true,width:'630px',height:'500px'},

    contentKwargs: function(sourceNode, attributes) {
        var mainpars = objectExtract(attributes,'condition,condition_kwargs');    
        for(var k in mainpars){
            sourceNode.gnrwdg[k] = mainpars[k];
        }
        if(!('configurator' in attributes)){
            attributes.configurator = this.default_configurator_pars;
            attributes.configurator.title = attributes.conf_title || _T('Report '+attributes.table+' configurator');
        }
        return attributes;
    },


    gnrwdg_viewerFrame:function(frame){
        //override
        var gnrwdg = this;
        var userObjectId = this.startUserObjectIdOrCode;
        var cpkw = {side:'center',overflow:'hidden',remote:'_rh_viewer',
                    remote_table:this.table,
                    remote_condition:this.condition,
                    remote_userObjectId:userObjectId,
                    remote_confPaletteCode:gnrwdg.conf_paletteCode,
                    remote_py_requires:'gnrcomponents/reporthandler/reporthandler:ReportHandler',
                    remote__onRemote:function(){
                        //gnrwdg.sourceNode.fireEvent('.built_viewer',true);
                        if(userObjectId){
                            gnrwdg.loadObject(userObjectId,true);
                        }
                    }};
        frame._('ContentPane',cpkw);
    },

    gnrwdg_configuratorFrame:function(frame,kw){
        var cpkw = {side:'center',overflow:'hidden',remote:'_rh_configurator',
                              remote_table:this.table,
                              remote_condition:this.condition,
                              remote_rootId:this.sourceNode.attr.nodeId,
                              remote_py_requires:'gnrcomponents/reporthandler/reporthandler:ReportHandler'};
        //cpkw.remote_query_pars = normalizeKwargs(kw,'condition');
        frame._('ContentPane',cpkw);
    },

    gnrwdg_userObjectData:function(){
        //override
        return this.sourceNode.getRelativeData('.stats.conf').deepCopy();
    },

    gnrwdg_onLoadingObject:function(userObjectId,fistLoad){
        //override
    },

    gnrwdg_onLoadedObject:function(result,userObjectId,fistLoad){
        //override
        //if(userObjectId=='__newobj__'){
        //    var conf = this.sourceNode.getRelativeData('.stats.conf');
        //    var fields = conf.getItem('fields');
        //    var n;
        //    ['rows','columns','values'].forEach(function(k){
        //        conf.getItem(k).keys().forEach(function(f){
        //            n = conf.getItem(k).popNode(f);
        //            fields.setItem(f,n._value,n.attr);
        //        });
        //    });
        //}else{
        //    this.sourceNode.setRelativeData('.stats.conf',result || new gnr.GnrBag());
        //}
        
    }
});