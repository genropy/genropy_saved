var iframeHandler = {
    setInLocalIframe: function(url){
        if(window.parent && window.parent!==window){
            window.parent.postMessage({topic:'setInLocalIframe',url:url},'*');
        }else{
            window.open(iframeHandler.parseUrl(url), 'Example');
        }
    },
    setZoom:function(kw){
        console.log('setZoom',kw)
    },
    parseUrl:function(url){
        var l = url.split(':');
        var result;
        if(l[0]=='version'){
            var curr = window.location.pathname;
            curr = curr.replace('/docu/index/rst','/webpages/docu_examples');
            curr+='/'+l[1]+'?_source_viewer=true';
            return curr;
        }else{
            result = l[1];
        }
        return result;
    },
    setClientWidth:function(kw){
        document.body.style.width = kw.width +'px';
    }
}
var localIframe = iframeHandler.setInLocalIframe;

window.addEventListener("message", function(e){
    if(e.data){
        iframeHandler[e.data.topic](e.data);
    }
}, false);