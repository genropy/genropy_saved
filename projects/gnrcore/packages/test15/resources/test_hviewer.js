var treeCompanion = {
    labelCb:function(item,maxwidth){
        var right = ['superficie:8','popolazione:10'];
        var k = 10;
        var kw = {}
        if(item.attr.description){
            kw.description = item.attr.description;
        }else{
            kw.description = item.attr.codice_comune +'-'+ item.attr.denominazione;
        }
        kw.superficie = item.attr.superficie || 0;
        kw.popolazione = item.attr.popolazione_residente || 0;
        var l = [];
        l.push('<div class="treecell" style="left:0;">'+kw.description+'</div>');
        currx = 0;
        right.reverse().forEach(function(n){
            n = n.split(':')
            var content = kw[n[0]];
            var width = n[1];

            l.push('<div class="treecell" style="right:'+currx+'em;width:'+(width-1)+'em;text-align:right;">'+content+'</div>');
            currx+=width || 0;
        })
        rowwidth = maxwidth-item.attr.level*k;
        return "innerHTML:<div class='treerow' style='width:"+rowwidth+"px;'>"+l.join('')+"</div>";
    }
}