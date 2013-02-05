var dynamicFormHandler = {
    onDataTypeChange:function(sourceNode,data_type,reason,newrecord){
        var allowedWidget,allowedFormat,defaults;
        if(data_type=='T'){
            allowedWidget = 'textbox:TextBox,simpletextarea:TextArea,filteringselect:Filtering Select,combobox:ComboBox,dbselect:DbSelect,checkboxtext_nopopup:Checkboxtext,checkboxtext:Popup Checkboxtext,geocoderfield:GeoCoderField';
            allowedFormat = '';
            defaults = {wdg_tag:'textbox',format:''};
        }else if(data_type=='L'){
            allowedWidget = 'numbertextbox:NumberTextBox,numberspinner:NumberSpinner,horizontalslider:Slider,filteringselect:Filtering Select,combobox:Combobox';
            allowedFormat = '###0\n0000';
            defaults = {wdg_tag:'numbertextbox',format:''};
        }else if(data_type=='N'){
            allowedWidget = 'numbertextbox:NumberTextBox,currencytextbox:CurrencyTextBox,numberspinner:NumberSpinner,horizontalslider:Slider,filteringselect:Filtering Select,combobox:Combobox';
            allowedFormat = '###0\n0000.000';
            defaults = {wdg_tag:'numbertextbox',format:''};
        }else if(data_type=='D'){
            allowedWidget = 'datetextbox:Popup,datetextbox_nopopup:Plain';
            allowedFormat = 'short,medium,long';
            defaults = {wdg_tag:'datetextbox',format:'short'};

        }else if(data_type=='H'){
            allowedWidget = 'timetextbox:Calendar Popup,timetextbox_nopopup:Date field';
            allowedFormat = 'short,medium,long';
            defaults = {wdg_tag:'timetextbox',format:'short'};
        }else if(data_type=='B'){
            allowedWidget = 'checkbox:CheckBox,filteringselect:FilteringSelect';
            allowedFormat = 'Yes,No\nTrue,False';
            defaults = {wdg_tag:'checkbox',format:'Yes,No'};

        }else if(data_type=='P'){
            allowedWidget = 'img:Image';
            allowedFormat = ''
            defaults = {wdg_tag:'img',format:'auto'};

        }else if(data_type=='GR'){
            allowedWidget = 'GR:Grafico';
            allowedFormat = ''

            defaults = {wdg_tag:'GR',format:'auto'};
        }
        sourceNode.setRelativeData('#FORM.allowedWidget',allowedWidget);
        sourceNode.setRelativeData('#FORM.allowedFormat',allowedFormat);
        if(reason!='container' || newrecord){
            for (var k in defaults){
                sourceNode.setRelativeData('#FORM.record.'+k,defaults[k]);
            }
        }
    },
    onSetWdgTag:function(sourceNode,wdg_tag){
        var calculated = sourceNode.getRelativeData('.calculated');
        if(!calculated){
            sourceNode.setRelativeData('#FORM.boxClass','dffb_enterable dffb_'+wdg_tag);
        }else{
            sourceNode.setRelativeData('#FORM.boxClass','dffb_calculated');
        }
    },
    
    onSetCalculated:function(sourceNode,calculated){
        var wdg_tag,boxClass;
        boxClass = 'dffb_enterable';
        if(calculated){
            boxClass = 'dffb_calculated';
        }else{
                //formclass = 'dffb_'+data_type;
        }
        sourceNode.setRelativeData('#FORM.boxClass',boxClass);
    },
    executeFormula:function(sourceNode,expression,extractstr){
        try{
            var kw = objectUpdate({},sourceNode.attr); 
            if(extractstr){
                objectExtract(kw,extractstr);
            }
            return funcApply('return '+expression,sourceNode.evaluateOnNode(kw),sourceNode);
        }catch(e){
            alert("Wrong formula:"+e.toString());
            return 'error';
        }
    },
    loadGrafico: function(node, formula, extractstr){
        var f = function(){
            var formula = this.attr._expression;
            var dati_da_graficare = [];
            formula = formula.split(';');
            var labels = [];
            
            for(var i = 0; i < formula.length; i++){
                var formula_series = formula[i].split(',');
                var dati_series = [];
                var indice = 0;
                var label = [];
                for(var j = 0; j < formula_series.length; j++){
                    var lbl = this.getRelativeData('.'+formula_series[j]+'?_valuelabel')
                    var value = this.getRelativeData('.'+formula_series[j]) || 0;
                    dati_series.push([indice, parseFloat(value)]);
                    indice++;
                    label.push(lbl);
                }
                dati_da_graficare.push(dati_series);
                labels.push(String(label.join(', ')))
            }
            dati_da_graficare = JSON.stringify(dati_da_graficare);
            labels = JSON.stringify(labels);
            
            
            return genro.makeUrl('/sys/dojoGraph', {dati_da_graficare:dati_da_graficare, labels:labels})
            //return genro.makeUrl('/grafico_dojo', {dati_da_graficare:dati_da_graficare, labels:labels})
        }
        var kw = objectUpdate({},node.attr); 
        if(extractstr){
            objectExtract(kw,extractstr);
        }
        return funcApply(f,node.evaluateOnNode(kw),node);
    },
    plotGraficoDojo: function(dati_da_graficare, labels){
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

            /*CREAZIONE DI UN PLOT*/
            chart.addPlot("default", {type: "Lines", hAxis:'x', vAxis:'y', markers:true, tension:3});

            var numero_parametri_graficati = 1;

            //Colori delle lines
            var colori_lines = ['','#000000','#d0ff8a','#61bbff','#95fc8d','#face8c','#E0AFEE','#FFFF66','#F984E5','#FFD700','#98FF98','#ff6666','#E0FFFF','#FF7F50','#99CBFF','#F0DC82','#FFE4C4']

            chart.addAxis("x")
            chart.addAxis("y", {vertical: true});

            var timestamp_precedente = 0;

            /*AGGIUNTA DI UNA SERIE DI DATI AL PLOT DESIDERATO*/
            for(var i = 0; i < dati_da_graficare.length; i++){
                var dati = [];
                var serie = dati_da_graficare[i];
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
};