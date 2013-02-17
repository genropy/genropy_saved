//dojo.require("dojox.charting.Chart2D");
//dojo.require("dojox.charting.themes.PlotKit.blue");
//dojo.require("dojox.charting.themes.PlotKit.cyan");
//dojo.require("dojox.charting.themes.PlotKit.green");
//dojo.require("dojox.charting.themes.PlotKit.orange");
//dojo.require("dojox.charting.themes.PlotKit.purple");
//dojo.require("dojox.charting.themes.PlotKit.red");
//dojo.require("dojox.charting.themes.ET.greys");



var gnrgraph = {

    test:function(iframe,testh,testw){
            var w = iframe.domNode.contentWindow;
            var doc = w.document;
            var d18 = w.dojo;
            var root = d18.byId('chart_root');
            var c = doc.createElement('div');
            c.setAttribute('id','test')
            c.style.height = '500px';
            c.style.width = '500px';
            c.style.background ='red'
            root.appendChild(c);
            d18.require(["dojox/charting/Chart", "dojox/charting/axis2d/Default", "dojox/charting/plot2d/StackedAreas", "dojox/charting/themes/Wetland" , "dojo/ready"],
  function(Chart, Default, StackedAreas, Wetland, ready){
    ready(function(){
      var c = new Chart("test");
      c.addPlot("default", {type: StackedAreas, tension:3})
        .addAxis("x", {fixLower: "major", fixUpper: "major"})
        .addAxis("y", {vertical: true, fixLower: "major", fixUpper: "major", min: 0})
        .setTheme(Wetland)
        .addSeries("Series A", [1, 2, 0.5, 1.5, 1, 2.8, 0.4])
        .addSeries("Series B", [2.6, 1.8, 2, 1, 1.4, 0.7, 2])
        .addSeries("Series C", [6.3, 1.8, 3, 0.5, 4.4, 2.7, 2])
        .render();
    });
});
    },

    start:function(name){
       
    }
}

/*dojo.declare("gnr.widgets.TooltipPane", gnr.widgets.gnrwdg, {
    createContent:function(sourceNode, kw, children) {

    },
    loadGraph: function(node, formula, extractstr){
        var f = function(){
            var formula = this.attr._expression;
            var data = [];
            formula = formula.split(';');
            var labels = [];
            
            for(var i = 0; i < formula.length; i++){
                var formula_series = formula[i].split(',');
                var series = [];
                var idx = 0;
                var label = [];
                for(var j = 0; j < formula_series.length; j++){
                    var lbl = this.getRelativeData('.'+formula_series[j]+'?_valuelabel')
                    var value = this.getRelativeData('.'+formula_series[j]) || 0;
                    series.push([idx, parseFloat(value)]);
                    idx++;
                    label.push(lbl);
                }
                data.push(series);
                labels.push(String(label.join(', ')))
            }
            data = JSON.stringify(data);
            labels = JSON.stringify(labels);
            
            
            return genro.makeUrl('/sys/dojoGraph', {data:data, labels:labels})
            //return genro.makeUrl('/grafico_dojo', {data:data, labels:labels})
        }
        var kw = objectUpdate({},node.attr); 
        if(extractstr){
            objectExtract(kw,extractstr);
        }
        return funcApply(f,node.evaluateOnNode(kw),node);
    },
    plotGraficoDojo: function(data, labels){
        dojo.require('dojox.charting.Theme');
        dojo.require("dojox.charting.action2d.MouseZoomAndPan")
        dojo.require("dojo.number");
        dojo.require( "dojo.date.locale" );
        dojo.require("dojox.charting.plot2d.Grid");
        dojo.require("dojox.charting.Chart");
        dojo.require("dojox.charting.axis2d.Default");
        dojo.require("dojox.charting.plot2d.Lines");
        dojo.require("dojox.charting.Chart2D");
        dojo.require("dojox.charting.action2d.Tooltip");
        dojo.require("dojox.charting.action2d.Magnify");
        dojo.require("dojo.colors");
        dojo.require("dojox.charting.widget.SelectableLegend");

        var chart = null;

        dojo.ready(function(){

            chart = new dojox.charting.Chart("chart");

            chart.addPlot("default", {type: "Lines", hAxis:'x', vAxis:'y', markers:true, tension:3});

            var numero_parametri_graficati = 1;

            //Colori delle lines
            var colori_lines = ['','#000000','#d0ff8a','#61bbff','#95fc8d','#face8c','#E0AFEE','#FFFF66','#F984E5','#FFD700','#98FF98','#ff6666','#E0FFFF','#FF7F50','#99CBFF','#F0DC82','#FFE4C4']

            chart.addAxis("x")
            chart.addAxis("y", {vertical: true});

            var timestamp_precedente = 0;

            for(var i = 0; i < data.length; i++){
                var dati = [];
                var serie = data[i];
                if(serie[0].length == 2){
                    for(var j = 0; j < serie.length; j++){
                        var x_value = serie[j][0];
                        var value = serie[j][1];
                        var label = labels[i].split(',') 
                        var tooltip = ['<table>'];
                        tooltip.push('<tr><td>Nome:</td><td><b>'+label[j].trim()+'</b></td></tr>')
                        tooltip.push('<tr><td>Valore:</td><td><b>'+value+'</b></td></tr>');
                        tooltip.push('</table>');
                        tooltip = tooltip.join('');

                        dati.push({x:x_value, y:value, tooltip: tooltip})
                    }
                    //, stroke: {color:"blue"}
                    new dojox.charting.action2d.MouseZoomAndPan(chart, "default", { axis: "x", keyZoomModifier: "alt" });
                    chart.addSeries(labels[i], dati, {plot:'default', stroke:{width:2, color:colori_lines[numero_parametri_graficati]}});

                    numero_parametri_graficati++;

                }
            }

            var objectA = new dojox.charting.action2d.Magnify(chart, 'default', {scale: 3});
            var objectB = new dojox.charting.action2d.Tooltip(chart, 'default');      

            chart.render();
            var legenda = new dojox.charting.widget.SelectableLegend({chart: chart, horizontal: true}, "legenda");
        });
    }
});
*/