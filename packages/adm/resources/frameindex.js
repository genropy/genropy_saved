var frameIndex = {};

frameIndex.selectIframePage=function(sourceNode,name,label,file,table,formResource,viewResource){
    var sc = genro.nodeById("center_stack");
    var page = sc.getValue().getItem(name);
    var url;
    if(!page){
         page = sc._('ContentPane',name,{pageName:name,title:label,overflow:'hidden',nodeId:name});
         url = file;
         var urlPars = {inframe:true};
         if(table){
            url = '/adm/th/thrunner/'+table.replace('.','/');
            if(formResource){
                urlPars['th_formResource'] = formResource;
            }
            if(viewResource){
                urlPars['th_viewResource'] = viewResource;
            }
         }
         url = genro.addParamsToUrl(url,urlPars);
    }
    sourceNode.setRelativeData('selectedFrame',name);
    if(url){
        setTimeout(function(){page._('iframe',{'height':'100%','width':'100%','border':0,src:url});},1);
    }
}