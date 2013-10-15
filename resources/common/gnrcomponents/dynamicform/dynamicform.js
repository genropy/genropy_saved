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
            allowedWidget = 'graph:Graph';
            allowedFormat = ''

            defaults = {wdg_tag:'graph',format:'auto'};
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
            for (var attr in kw) {
                var v = kw[attr];
                kw[attr] = sourceNode.currentFromDatasource(v);
                kw['F_'+attr] = '';
                if(typeof(v) == 'string' && v!='' && v.indexOf('==')!=0 && (v[0]=='^' || v[0]=='=')){
                    var formattedVal = sourceNode.currentFromDatasource(v+'?_formattedValue');
                    var displayedVal = sourceNode.currentFromDatasource(v+'?_displayedValue');
                    if(formattedVal || displayedVal){
                        kw['F_'+attr] = formattedVal || displayedVal;
                    }
                }
            }
            var result = funcApply('return '+expression,kw,sourceNode);
            var result_type= sourceNode.attr.result_type;
            if((result_type=='N' || result_type=='L' || result_type=='R') && isNaN(result)){
                result = null;
            }
            return result;
        }catch(e){
            alert("Wrong formula:"+e.toString());
            return 'error';
        }
    }
};