var genro = {};
genro.dom = {
    loadCss: function(url, cssTitle, cb) {
        var e = document.createElement("link");
        e.href = url;
        e.type = "text/css";
        e.rel = "stylesheet";
        e.media = "screen";
        document.getElementsByTagName("head")[0].appendChild(e);
        if (cb) e.onload = cb;
    },
    loadJs: function(url, cb) {
        var e = document.createElement("script");
        e.src = url;
        e.type = "text/javascript";
        document.getElementsByTagName("head")[0].appendChild(e);
        
        if (cb) {
            e.onload = cb;
            }
    }
}