var dynamicFormHandler = {
    onDataTypeChange:function(sourceNode,data_type,reason,newrecord){
        var allowedWidget,allowedFormat,defaults;
        if(data_type=='T'){
            allowedWidget = 'textbox:TextBox,simpletextarea:TextArea,filteringselect:Filtering Select,combobox:ComboBox,dbselect:DbSelect,checkboxtext_nopopup:Checkboxtext,checkboxtext:Popup Checkboxtext';
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

        }else if(data_type='P'){
            allowedWidget = 'imguploader:Image Uploader';
            allowedFormat = ''
            defaults = {wdg_tag:'imguploader',format:''};
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
            wdg_tag = 'div';
            boxClass = 'dffb_calculated';
            sourceNode.setRelativeData('.wdg_tag',null);
        }else{
                //formclass = 'dffb_'+data_type;
        }
        sourceNode.setRelativeData('#FORM.boxClass',boxClass);
    },
    
    onFieldsBagUpdated:function(kw){
        var data = kw.data;
        var templates = kw.templates;
        data.popNode('_df_summaries');
        var summaries = new gnr.GnrBag();
        var autotemplate =data.getItem('_df_autotemplate');
        if(autotemplate){
            var at = [];
            var r,vn;
            dojo.forEach(autotemplate.split(','),function(n){
                r = n.split(':');
                vn = data.getNode(r[1]);
                if(vn && vn._value+''){
                    at.push(r[0]+': '+(vn.attr._formattedValue || vn.attr._displayedValue || vn.getValue()));
                }
            })
            summaries.setItem('auto',at.join('<br/>'));
        };
        
        if(templates){
            templates.forEach(function(n){
                var tpl = n.getValue().getItem('tpl');
                if(tpl){
                    summaries.setItem(n.label,dataTemplate(tpl,data));
                }
            },'static');
        }
        data.setItem('_df_summaries',summaries);
        
        
        
    }
};