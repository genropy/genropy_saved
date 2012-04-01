var dynamicFormHandler = {
    onDataTypeChange:function(sourceNode,data_type){
        var allowedWidget,allowedFormat,defaults;
        if(data_type=='T'){
            allowedWidget = 'textbox:TextBox,simpletextarea:TextArea,filteringselect:Filtering Select,combobox:ComboBox,dbselect:DbSelect,checkboxtext:Multi checkbox';
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
            allowedWidget = 'timetextbox:Popup,timetextbox_nopopup:Plain';
            allowedFormat = 'short,medium,long';
            defaults = {wdg_tag:'timetextbox',format:'short'};
        }else if(data_type=='B'){
            allowedWidget = 'checkbox:CheckBox,filteringselect:FilteringSelect';
            allowedFormat = 'Yes,No\nTrue,False';
            defaults = {wdg_tag:'checkbox',format:'Yes,No'};

        }else if(data_type='P'){
            
        }
        sourceNode.setRelativeData('#FORM.allowedWidget',allowedWidget);
        sourceNode.setRelativeData('#FORM.allowedFormat',allowedFormat);
        for (var k in defaults){
            sourceNode.setRelativeData('#FORM.record.'+k,defaults[k]);
        }

    },
    onSetWdgTag:function(sourceNode,wdg_tag){
        if(wdg_tag!='div'){
            sourceNode.setRelativeData('#FORM.boxClass','dffb_enterable dffb_'+wdg_tag);
        }
    },
    
    onSetCalculated:function(sourceNode,calculated){
        var wdg_tag,boxClass;
        boxClass = 'dffb_enterable';
        if(calculated){
            wdg_tag = 'div';
            boxClass = 'dffb_calculated';
        }else{
                //formclass = 'dffb_'+data_type;
        }
        sourceNode.setRelativeData('.wdg_tag',wdg_tag);
        sourceNode.setRelativeData('#FORM.boxClass',boxClass);
    }
};