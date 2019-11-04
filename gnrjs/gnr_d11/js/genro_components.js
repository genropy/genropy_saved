//GNRWDG WIDGET DEFINITION BASE
dojo.declare("gnr.widgets.gnrwdg", null, {
    constructor: function(application) {
        this._domtag = 'div';
    },

    _beforeCreation: function(attributes, sourceNode) {
        sourceNode.gnrwdg = objectUpdate({'gnr':this,'sourceNode':sourceNode},objectExtract(this,'gnrwdg_*',true));
        attributes = sourceNode.attr;
        sourceNode._saved_attributes = objectUpdate({},attributes);
        sourceNode.attr = {};
        sourceNode.attr.tag = objectPop(attributes,'tag');
        var catchersHandlers = objectExtract(this,'gnrwdg_catch_*',true);
        sourceNode.gnrwdg.catchers = {};
        for (var k in sourceNode._dynattr){
            if(this['gnrwdg_set'+stringCapitalize(k)]){
                sourceNode.attr[k] = attributes[k];
            }else{
                for(var c in catchersHandlers){
                    if(k.indexOf(c+'_')===0){
                        sourceNode.attr[k] = attributes[k];
                        sourceNode.gnrwdg.catchers[k] = 'catch_'+c;
                        break;
                    }
                }
            }
        }
        var datapath=objectPop(attributes,'datapath');
        if(datapath){sourceNode.attr.datapath=datapath;}
        else if(datapath===false){
            sourceNode.attr.datapath = '';
        }

        var contentKwargs = this.contentKwargs(sourceNode, attributes);
        if (!this.createContent) {
            return false;
        }
        sourceNode.freeze();
        var children = sourceNode.getValue();
        sourceNode._value = null; // remove content that will be used in the inner construction
        var subTagItems = this.subtags?this.popSubTagItems(sourceNode.attr.tag,children):{};
        var content = this.createContent(sourceNode, contentKwargs,children,subTagItems);
        genro.assert(content,'create content must return');
        content.concat(children);
        sourceNode._isComponentNode=true;
        genro.src.stripData(sourceNode);
        sourceNode.unfreeze(true);
        return false;
    },

    popSubTagItems:function(maintag,children){
        var result = {};
        for (var tag in this.subtags){
            var sc = children._nodes.filter(function(n){
                return n.attr.tag == (maintag+'_'+tag).toLowerCase();
            });
            var subtag_items = new gnr.GnrBag();
            sc.forEach(function(n){
                delete n.attr.tag;
                subtag_items.setItem(n.label,children.popNode(n.label));
            });
            subtag_items._subtag_handler = this.subtags[tag];
            result[tag] = subtag_items;
        }
        return result;
    },

    onStructChild:function(attributes,source) {
        var parentNode = source.getParentNode();
        var attr = parentNode?parentNode.attr:{};
        if (attr.datapath==null && attributes.datapath==null) {
            var defaultDatapath = this.defaultDatapath(attributes);
            if (defaultDatapath) {
                attributes.datapath = defaultDatapath;
            }
        }

    },
    contentKwargs: function(sourceNode, attributes) {
        return attributes;
    },
    defaultDatapath:function(attributes) {
        return null;
    },

    cell_onCreating:function(gridEditor,colname,colattr){
        //override
    },

    cell_onDestroying:function(sourceNode,gridEditor,editingInfo){
        //override
    },
   //gnrwdg_isVisible:function(){
   //    
   //}
});

dojo.declare("gnr.widgets.TooltipPane", gnr.widgets.gnrwdg, {
    createContent:function(sourceNode, kw, children) {
        var ddbId = kw.openerId || sourceNode.getStringId();
        var modifiers = objectPop(kw,'modifiers') || '*';
        var onOpening = objectPop(kw,'onOpening');
        var onClosing = objectPop(kw,'onClosing');

        var modal = objectPop(kw,'modal');
        if (onOpening){
            onOpening = funcCreate(onOpening,'e,sourceNode,dialogNode,kwargs',sourceNode);
        }
        if (onClosing){
            onClosing = funcCreate(onClosing,'e,sourceNode,dialogNode,kwargs',sourceNode);
        }
        var evt = objectPop(kw,'evt') || 'onclick';
        var parentDomNode;
        var sn = sourceNode;
        var placingId = objectPop(kw,'placingId'); 
        var noConnector = objectPop(kw,'noConnector');
        while(!parentDomNode){
            sn = sn.getParentNode();
            parentDomNode = sn.getDomNode();
        }
        var ddkw = {hidden:true,nodeId:ddbId,modifiers:modifiers,evt:evt,modal:modal,
                                selfsubscribe_open:function(kw){
                                    if(!onOpening || onOpening(kw.evt,kw.domNode.sourceNode,this._value.getNode('ttd'),kw)!==false){
                                        this.widget.dropDown._lastEvent=kw.evt;
                                        this.widget._openDropDown(kw.domNode);
                                    }
                                },
                                selfsubscribe_close:function(kw){
                                    if(!onClosing || onClosing(kw.evt,kw.evt.target.sourceNode,this._value.getNode('ttd'),kw)!==false){
                                        this.widget._closeDropDown();
                                    }
                                }};
        if(placingId){
            ddkw.onOpeningPopup = function(openKw,evtDomNode){
                                    var placingDomNode = genro.domById(placingId);
                                    if(placingDomNode){
                                        openKw.around = placingDomNode;
                                        openKw.popup.domNode.setAttribute('connector',"none");
                                        //dojo.removeClass(openKw.popup.domNode,'dijitTooltipBelow');
                                    }
                                };
        }
        var ddb = sourceNode._('dropDownButton',ddkw);

        kw['connect_onOpen'] = function(){
            var wdg = this.widget;
            if(modal){
                genro.nodeById('_gnrRoot').setHiderLayer(true,{z_index:1000,opacity:kw.hiderOpacity || 0,
                                                connect_onclick:function(evt){
                                                    genro.publish({topic:'close',nodeId:ddbId},{evt:evt});
                                                }
                                                                });
            }
            setTimeout(function(){
                wdg.resize();
            },1)
        };
        if(modal){
            kw['connect_onClose'] = function(){
                genro.nodeById('_gnrRoot').setHiderLayer(false);
            };
            kw.z_index = 1001;
        }   
        kw.doLayout = true;
        var tdialog =  ddb._('TooltipDialog','ttd',kw);
        dojo.connect(parentDomNode,evt,function(e){
            if(genro.wdg.filterEvent(e,modifiers)){
                genro.publish(ddbId+'_open',{'evt':e,'domNode':e.target});
            } 
        });
        return tdialog;
    }
});

dojo.declare("gnr.widgets.MenuDiv", gnr.widgets.gnrwdg, {
    createContent:function(sourceNode, kw, children){
        var buttonkw = objectExtract(kw,'btn_*');
        var iconClass = objectPop(kw,'iconClass');
        var label = objectPop(kw,'label');
        var disabled = objectPop(kw,'disabled');
        var parentForm = objectPop(kw,'parentForm');
        buttonkw.hidden = objectPop(kw,'hidden');

        var tip = objectPop(kw,'tip');
        iconClass = iconClass? 'iconbox ' +iconClass :null;
        var box_kw = objectUpdate({_class:'menuButtonDiv buttonDiv',disabled:disabled,tip:tip},buttonkw);
        if(parentForm){
            box_kw.parentForm = parentForm;
        }
        var box = sourceNode._('div',box_kw);
        if(label && !iconClass){
            //not well implemented
            box._('div',objectUpdate({innerHTML:label,display:'inline-block'},objectExtract(kw,'label_*')));
        }
        if(iconClass){
            box._('div',{_class:iconClass});
        }

        kw._class = kw._class || 'smallmenu';
        kw.modifiers = kw.modifiers || '*';
        return box._('menu',kw);
    }
});

dojo.declare("gnr.widgets.ColorTextBox", gnr.widgets.gnrwdg, {
    createContent:function(sourceNode, kw, children){
        var chromapars = objectExtract(kw,'colors,steps,menupath,mode,extraLines');
        var gnrwdg = sourceNode.gnrwdg;
        kw._autoselect=true;
        sourceNode.attr._workspace = true;
        sourceNode.attr.mode = chromapars.mode;
        sourceNode.attr.colors = chromapars.colors;
        sourceNode.attr.steps = chromapars.steps;
        gnrwdg.extraLines = chromapars.extraLines;
        gnrwdg.menupath = chromapars.menupath || '#WORKSPACE.colormenu';
        var value = kw.value;
        if(!value){
            console.error('Missing value in ColorTextBox');
            return;
        }
        kw.background = '^#WORKSPACE.currentBackground';
        kw.color = '^#WORKSPACE.currentForeground';
        var tb = sourceNode._('textbox',kw);
        gnrwdg.tbNode = tb.getParentNode();
        tb._('comboMenu',{'storepath':gnrwdg.menupath,
                          '_class':'menupane colormenu',
                          'selected_color':value.replace('^','')
                     });
        tb._('dataController',{script:'sn.gnrwdg.setTextBoxColors();','v':kw.value,sn:sourceNode});
        if(!window.chroma){
            genro.dom.loadJs('/_rsrc/js_libs/chroma.min.js',function(){
                gnrwdg.loadMenuData();
                gnrwdg.setTextBoxColors();
            });
        }else{
            gnrwdg.loadMenuData();
            gnrwdg.setTextBoxColors();
        }
        return tb;
    },

    gnrwdg_setTextBoxColors:function(){
        var tbNode = this.sourceNode.gnrwdg.tbNode;
        this.sourceNode.setRelativeData('^#WORKSPACE.currentBackground',null);
        this.sourceNode.setRelativeData('^#WORKSPACE.currentForeground',null);
        var v = tbNode.getAttributeFromDatasource('value');

        if(!v){
            tbNode.setAttributeInDatasource('value',null);
            return;
        }
        var c;
        try{
            c = chroma(v);
        }catch(e){
            return;
        }
        var mode = this.sourceNode.getAttributeFromDatasource('mode') || 'hex';
        var csscolor = mode=='rgba'? c.css():c.hex();
        if(csscolor!=v){
            if(this.tbNode.widget){
                this.tbNode.widget.setValue(csscolor,true);
            }
        }
        var foreground = chroma.contrast(csscolor,"white")>chroma.contrast(csscolor,"#444")?"white":"#444";
        this.sourceNode.setRelativeData('^#WORKSPACE.currentBackground',csscolor);
        this.sourceNode.setRelativeData('^#WORKSPACE.currentForeground',foreground);
    },

    gnrwdg_loadMenuData:function(){
        var kw = this.sourceNode.currentAttributes();
        var mode = kw.mode || 'hex';
        var b = new gnr.GnrBag();
        var colors = kw.colors || genro.getData('app_preference.sys.theme.palette_colors') || 'black,white,red,green,yellow,blue,purple';
        var steps = kw.steps || genro.getData('app_preference.sys.theme.palette_steps') || 20;
        var s = chroma.scale(colors.split(',')).colors(steps);
        var foreground,caption,csscolor,colorcaption;
        var rescontent;
        var opSteps = [1.0,0.9,0.8,0.7,0.6,0.5,0.4,0.3,0.2,0.1];
        var opacityCb = function(color,foregroundColor){
            var result = new gnr.GnrBag();
            opSteps.forEach(function(v,idx){
                var hcolor = chroma(color).alpha(v);
                var hf = v>=0.5?foregroundColor:"#444";
                var hcsscolor = hcolor.css();
                var hcaption = '<div style="width:5em;text-align:right;padding-right:5px;background:'+hcsscolor+';"><div style="display:inline-block;font-family:courier;color:'+hf+'">'+v*100+'%</div></div>';
                result.setItem('r_'+idx,null,{caption:hcaption,color:hcsscolor,foregroundColor:hf});
            });
            return result;
        };
        var l = s.forEach(function(n,idx){
            foreground = chroma.contrast(n,"white")>chroma.contrast(n,"#444")?"white":"#444";
            csscolor = n;
            rescontent = null;
            if(mode=='rgba'){
                csscolor = chroma(n).css();
                var c = n;
                var fc = foreground;
                rescontent = new gnr.GnrBagCbResolver({method:function(){
                    return opacityCb(c,fc);
                }},true);
            }
            caption = '<div style="width:100%;text-align:left;padding-left:5px;background:'+csscolor+';"><div style="display:inline-block;font-family:courier;color:'+foreground+'">'+csscolor+'</div></div>';
            b.setItem('r_'+idx,rescontent,{caption:caption,color:csscolor,foregroundColor:foreground});
        });
        if(this.extraLines){
            b.setItem('r_'+b.len(),null,{caption:'-'});

            this.extraLines.split(',').forEach(function(l,idx){
                b.setItem('r_'+b.len(),null,{caption:l,color:l});
            });
        }
        this.sourceNode.setRelativeData(this.menupath,b);
    },
    gnrwdg_setColors:function(){
        this.loadMenuData();
    },
    gnrwdg_setSteps:function(){
        this.loadMenuData();
    },
    gnrwdg_setMode:function(){
        this.loadMenuData();
    },
    cell_onCreating:function(gridEditor,colname,colattr) {
        console.log('cell_onCreating');

        //colattr['onCreated'] = 'this.widget.focusNode.focus()';
    },

    cell_onDestroying:function(sourceNode,gridEditor,editingInfo){
        console.log('cell_onDestroying');
    }
        

});

dojo.declare("gnr.widgets.ColorFiltering", gnr.widgets.gnrwdg, {

    createContent:function(sourceNode, kw, children){
        var value = kw.value;
        var gnrwdg = sourceNode.gnrwdg;
        sourceNode.attr._workspace = true;
        if(!value){
            console.error('Missing value in ColorTextBox');
            return;
        }
        kw.callback = function(kw){
            var _id = kw._id;
            var _querystring = kw._querystring;
            var colorsDict = chroma.colors;
            var data = objectKeys(colorsDict).sort().map(function(n){
                return {name:n,_pkey:colorsDict[n],color:'<div style="background:'+colorsDict[n]+';">&nbsp;&nbsp;<div>',caption:n};
            });
            var cbfilter = function(n){return true;};
            if(_querystring){
                _querystring = _querystring.slice(0,-1).toLowerCase();
                cbfilter = function(n){return n.name && n.name.toLowerCase().indexOf(_querystring)>=0;};
            }else if(_id){
                cbfilter = function(n){return n._pkey==_id;};
            }
            data = data.filter(cbfilter);
            return {headers:'name:Color,color:Sample',data:data};
        };
        kw.background = '^#WORKSPACE.currentBackground';
        kw.color = '^#WORKSPACE.currentForeground';
        kw.auxColumns='name,color';
        kw.hasDownArrow =true;
        kw.limit = 0;
        var tb = sourceNode._('callbackSelect',kw);
        gnrwdg.tbNode = tb.getParentNode();

        tb._('dataController',{script:'sn.gnrwdg.setTextBoxColors(v);','v':kw.value,sn:sourceNode});
        if(!window.chroma){
            genro.dom.loadJs('/_rsrc/js_libs/chroma.min.js',function(){
                gnrwdg.setTextBoxColors();
            });
        }else{
            gnrwdg.setTextBoxColors();
        }
        return tb;
    },

    gnrwdg_setTextBoxColors:function(){
        var tbNode = this.sourceNode.gnrwdg.tbNode;
        var v = tbNode.getAttributeFromDatasource('value');
        if(!v){
            tbNode.setAttributeInDatasource('value',null);
            return;
        }
        var foreground = chroma.contrast(v,"white")>chroma.contrast(v,"#444")?"white":"#444";
        this.sourceNode.setRelativeData('^#WORKSPACE.currentBackground',v);
        this.sourceNode.setRelativeData('^#WORKSPACE.currentForeground',foreground);
    },


});

dojo.declare("gnr.widgets.TooltipMultivalue", gnr.widgets.TooltipPane, {
    createContent:function(sourceNode, kw, children){
        var that = this;
        var textboxNode = sourceNode.getParentNode();
        textboxNode.attr.mask = '==this._getCurrentMask();';


        textboxNode._('span',{'innerHTML':textboxNode.attr.value+'?_formattedValue',_class:'formattedViewer',
                               _attachPoint:'focusNode.parentNode'});
        dojo.addClass(textboxNode.widget.focusNode.parentNode,'formattedTextBox');
       

        var valuepath = textboxNode.absDatapath(textboxNode.attr.value);
        var sourcepath = valuepath+'_mv';
        textboxNode._getCurrentMask = function(){
            var data = genro.getData(sourcepath);
            var mainNode = data?data.getNodeByValue('mv_main',true):null;
            if(!mainNode){
                return '';
            }
            return '%s<div class="mv_mask" >'+mainNode.getValue().getItem('mv_label')+'<div>';
        };
        textboxNode._mvhandler = this;
        textboxNode._onSettingValueInData = function(tn,value){that.onSetMainValue(tn,value);};
        var arrowNode = sourceNode._('comboArrow','arrowNode',{_class:'',iconClass:'mv_iconbox',width:'12px'});
        arrowNode._('dataController',{script:'genro.dom.setClass( this.getParentNode()._value.getNode("iconNode"),"mv_is_multi",(data&&data.len()>1));',data:'^'+sourcepath});

        var tooltipPars = objectExtract(kw,'tooltip_*');
        tooltipPars.onOpening=function(e,sourceNode,dialogNode){
            var data = genro.getData(sourcepath);
            that.onSetMainValue(textboxNode,textboxNode.widget.getValue());
            if(genro.dom.getEventModifiers(e)=='Shift'){
                that.openMultiValueEditor('new',textboxNode,{sourcepath:sourcepath,valuepath:valuepath});
                return false;
            }
            that.multivalueTable(dialogNode,textboxNode,{sourcepath:sourcepath,valuepath:valuepath});
        };
        var tt = arrowNode._('tooltipPane',tooltipPars);
        tt._('div','tooltipContent',{padding:'5px',connect_onclick:function(e){
            if(!sourceNode.form.isDisabled()){
                that.onSelectedRow(e,this,{sourcepath:sourcepath,valuepath:valuepath});
            }
        }, connect_ondblclick:function(e){
            if(!sourceNode.form.isDisabled()){
                var r = e.target.parentElement.getAttribute('r');
                that.openMultiValueEditor(r,textboxNode,{sourcepath:sourcepath,valuepath:valuepath});
            }
        }});
        return tt;
    },

    openMultiValueEditor:function(r,sourceNode,kw){
        var that = this;
        var title = sourceNode.attr.field_name_long;
        var data = genro.getData(kw.sourcepath);
        var labels = sourceNode._getMultiValue? sourceNode._getMultiValue():sourceNode.getAttributeFromDatasource('multivalue');
        var editedRow;
        if(r=='new'){
            editedRow = new gnr.GnrBag({mv_label:labels.split(',')[0]});
        }else{
            editedRow = data.getItem('#'+r).deepCopy();
        }
        genro.setData('gnr.multivalue.data',editedRow);
        var dlg = genro.dlg.quickDialog(title,{_showParent:true,width:'280px',datapath:'gnr.multivalue.data'});
        var bar = dlg.bottom._('slotBar',{slots:'2,deletebtn,*,cancel,confirm,2',action:function(){
                                                    dlg.close_action();
                                                    var result = genro.getData('gnr.multivalue').popNode('data').getValue();
                                                    if(this.attr.command=='delete' && r!='new'){
                                                        result.setItem('mv_value',null);
                                                    }
                                                    if(this.attr.command!='cancel'){
                                                        that.changeMultivalueRow(sourceNode,objectUpdate({result:result,r:r},kw));
                                                    }
                                                }});
        bar._('button','deletebtn',{'label':_T('Delete'),command:'delete'});
        bar._('button','cancel',{'label':_T('Cancel'),command:'cancel'});
        bar._('button','confirm',{'label':_T('Confirm'),command:'confirm'});
        var box = dlg.center._('div',{padding:'5px'});
        var fb = genro.dev.formbuilder(box,2,{border_spacing:'3px',width:'270px'});
        var b = fb.addField('div',{text_align:'right'})
        b._('div',{innerHTML:'^.mv_label',_class:'mv_labels'})
        b._('menu',{values:labels,action:'SET .mv_label=$1.label',modifiers:'*',_class:'smallmenu'});
        fb.addField('TextBox',{value:'^.mv_value',width:'13em'});
        fb.addField('div',{innerHTML:_T('Notes'),td_vertical_align:'top',text_align:'right'})
        fb.addField('SimpleTextArea',{value:'^.mv_note',width:'13em',colspan:2});
        dlg.show_action();
    },
    changeMultivalueRow:function(sourceNode,kw){
        var result = kw.result;
        result.forEach(function(n){
            n.attr = {};
        });
        var r = kw.r;
        var resultvalue = result.getItem('mv_value');
        var data = genro.getData(kw.sourcepath);
        if(r=='new' && resultvalue){
            data.setItem('#id',result);
        }else{
            var path = '#'+r;
            var editedNode = data.getNode(path);
            var databag = editedNode.getValue();
            var is_main = databag.getItem('is_main');
            databag.setItem('mv_label',result.getItem('mv_label'));
            databag.setItem('mv_value',resultvalue);
            databag.setItem('mv_note',result.getItem('mv_note'));
            genro.setData(kw.valuepath,resultvalue);
        }
        this.cleanMultivalueData(data);
    },

    onSetMainValue:function(textboxNode,value){
        value = value || '';
        var currvalue = textboxNode.getAttributeFromDatasource('value');
        var original_value = value;
        if(currvalue==value){
            return;
        }
        if(isNullOrBlank(value) && isNullOrBlank(currvalue)){
            return;
        }
        var labels = textboxNode._getMultiValue? textboxNode._getMultiValue():textboxNode.getAttributeFromDatasource('multivalue');
        var multivalues = textboxNode.getRelativeData(textboxNode.attr.value+'_mv');
        if (!multivalues){
            multivalues = new gnr.GnrBag();
            textboxNode.setRelativeData(textboxNode.attr.value+'_mv',multivalues,{});
        }
        var mainNode = multivalues.getNodeByValue('mv_main',true);
        var m;
        if(value.indexOf('@')>=0){
            m = value.match(/(\s*[A-Za-z\d\_\-\+\.]+@(?:[A-Za-z\d\_\-]+\.)+[A-Za-z]{2,})(\s+)?([A-Za-z]+)?(\s+)?([\w\s]+)?/);
        }else{
            m = value.match(/(^\s*\d+[\d\s\.\-\+\/]+)(\s+)?([A-Za-z]+)?(\s+)?([\w\s]+)?/);
        }
        var label,notes,r;
        if(m){
            value = m[1];
            label = m[3];
            notes = m[5];
            if(label){
                var k = labels.toLowerCase().split(',').indexOf(label.toLowerCase());
                if(k>=0){
                    label = labels.split(',')[k];
                }else{
                    notes = label+' '+notes;
                    label = null;
                }
            }
            notes = notes?notes.trim():null;
        }
        if(mainNode){
            r = mainNode._value;
            label = label || r.getItem('mv_label');
        }else{
            r = new gnr.GnrBag();
            multivalues.setItem('#id',r);
            label = label || labels.split(',')[0];
        }
        r.setItem('mv_value',value);
        r.setItem('mv_label',label);
        if(notes){
            r.setItem('mv_note',notes);
        }
        this.cleanMultivalueData(multivalues);
        setTimeout(function(){
            textboxNode.setRelativeData(textboxNode.attr.value,value);
        },1);

    },
    cleanMultivalueData:function(data){
        if(data){
            dojo.forEach(data.getNodes(),function(n){
                var r = n.getValue();
                if(!r || !r.getItem('mv_value')){
                    data.popNode(n.label);
                }
            });
            if(data.len()===0){
                data.getParentNode().setValue(null);
            }else if(data.len()==1 || !data.getNodeByValue('mv_main',true)){
                data.setItem('#0.mv_main',true);
            }
        }
    },
    multivalueTable:function(sourceNode,textboxNode,kw){
        var currmainvalue = textboxNode.widget.getValue();
        textboxNode.setRelativeData(kw.valuepath,currmainvalue);
        var data = genro.getData(kw.sourcepath);

        var contentDomNode = sourceNode._value.getNode('tooltipContent').domNode; 
        contentDomNode.innerHTML = this.multivalueHtmlFromData(data);
        return;
    },

    multivalueHtmlFromData:function(data){
        var tbody = [];
        var path,mv_main;
        var r =0;
        if(data){
            data.forEach(function(n){
                mv_main = n._value.getItem('mv_main')?'true':'false';
                tbody.push(dataTemplate('<tr r="'+r+'"><td mv_main="'+mv_main+'"></td><td>$mv_label</td><td>$mv_value</td><td>$mv_note</td><tr>',n._value));
                r++;
            });
        }
        tbody.push('<tr r="new"><td colspan="4"></td></tr>');
        return '<table class="mv_table"><tbody>'+tbody.join('')+'</tbody></table>';
    },
    onSelectedRow:function(e,sourceNode,kw){
        if(e.target.getAttribute('mv_main')=='false'){
            var data = genro.getData(kw.sourcepath);
            var r = e.target.parentElement.getAttribute('r');
            if(r=='new'){
                return;
            }
            data.getNodeByValue('mv_main',true)._value.setItem('mv_main',false)
            var newmain = data.getItem('#'+r);
            newmain.setItem('mv_main',true);
            genro.setData(kw.valuepath,newmain.getItem('mv_value'));
            sourceNode.domNode.innerHTML = this.multivalueHtmlFromData(data);
        }
    }


});

dojo.declare("gnr.widgets.Palette", gnr.widgets.gnrwdg, {
    contentKwargs: function(sourceNode, attributes) {
        var left = objectPop(attributes, 'left');
        var right = objectPop(attributes, 'right');
        var top = objectPop(attributes, 'top');
        var bottom = objectPop(attributes, 'bottom');
        var persist = objectPop(attributes, 'persist');

        var lazyContent = objectPop(attributes,'lazyContent');
        var paletteCode = objectPop(attributes,'paletteCode');
        if(paletteCode){
            attributes['datapath'] = attributes['datapath'] || 'gnr.palettes.'+paletteCode;
        }
        if ((left === null) && (right === null) && (top === null) && (bottom === null)) {
            this._last_floating = this._last_floating || {top:0,right:0};
            this._last_floating['top'] += 10;
            this._last_floating['right'] += 10;
            top = this._last_floating['top'] + 'px';
            right = this._last_floating['right'] + 'px';
        }
        var dockTo = objectPop(attributes, 'dockTo');
        var dockButton = objectPop(attributes,'dockButton') || objectExtract(attributes, 'dockButton_*');
        if(dockButton===true){
            dockButton = {iconClass:'iconbox app'};
        }
        if (objectNotEmpty(dockButton)){
            dockTo = 'dummyDock';
            if(!dockButton.label){
                dockButton._class = 'iconOnly slotButtonIconOnly';
            }
            attributes.dockButton = dockButton;
        }
        var floating_kwargs = objectUpdate(attributes, {dockable:true,closable:false,visibility:'hidden'});
        floating_kwargs['templateString'] ="<div class=\"dojoxFloatingPane\" id=\"${id}\"><div tabindex=\"0\" waiRole=\"button\" class=\"dojoxFloatingPaneTitle\" dojoAttachPoint=\"focusNode\"><span dojoAttachPoint=\"closeNode\" dojoAttachEvent=\"onclick: close\" class=\"dojoxFloatingCloseIcon\"></span><span dojoAttachPoint=\"maxNode\" dojoAttachEvent=\"onclick: maximize\" class=\"dojoxFloatingMaximizeIcon\"></span><span dojoAttachPoint=\"restoreNode\" dojoAttachEvent=\"onclick: _restore\" class=\"dojoxFloatingRestoreIcon\"></span><span dojoAttachPoint=\"dockNode\" dojoAttachEvent=\"onclick: minimize\" class=\"dojoxFloatingMinimizeIcon\"></span><span dojoAttachPoint=\"titleNode\" class=\"dijitInline dijitTitleNode\"></span></div><div dojoAttachPoint=\"canvas\" class=\"dojoxFloatingPaneCanvas\"><div dojoAttachPoint=\"containerNode\" waiRole=\"region\" tabindex=\"-1\" class=\"${contentClass}\"></div><span dojoAttachPoint=\"resizeHandle\" class=\"dojoxFloatingResizeHandle\"></span></div></div>";
        var showOnStart = false;
        if (dockTo === false) {
            floating_kwargs.closable = true;
            floating_kwargs.dockable = false;
            showOnStart = true;
        } else if (dockTo && dockTo.indexOf(':open') >= 0) {
            dockTo = dockTo.split(':')[0];
            objectPop(floating_kwargs, 'visibility');
            showOnStart = true;
        }
        floating_kwargs.subscribe_onClosePage=function(){
            this.widget.saveRect();
        };
        floating_kwargs.onCreated = function(widget) {
            setTimeout(function() {
                if(showOnStart){
                    widget.show();
                    widget.bringToTop();
                }
            }, 1);
        };
        if (!dockTo && dockTo !== false) {
            dockTo = 'default_dock';
        }
        if (dockTo) {
            floating_kwargs.dockTo = dockTo;
        }
        return objectUpdate({height:'350px',width:'300px',
            top:top,right:right,left:left,bottom:bottom,
            persist:persist,
            resizable:true}, floating_kwargs);
    },
    createContent:function(sourceNode, kw) {
        if (kw.dockTo == '*') {
            var dockId = sourceNode._id + '_dock';
            sourceNode._('dock', {id:dockId});
            kw.dockTo = dockId;
        }
        if (kw.dockButton){
            kw.dockButton['action'] = function(){
                var widget = genro.wdgById(kw.nodeId);
                widget.show();
                widget.bringToTop();
            };
            kw.dockButton['label'] = kw.dockButton['label'] || kw.title;
            kw.dockButton['showLabel'] = kw.dockButton['showLabel'] || !kw.dockButton.iconClass;
            sourceNode._('button', kw.dockButton);
        }
        if (kw.nodeId) {
            var that=this;
            kw.connect_show = function() {
                genro.publish(kw.nodeId + '_showing');
            };
            kw.connect_hide = function() {
                genro.publish(kw.nodeId + '_hiding');
            };
        }
        return sourceNode._('floatingPane', kw);
    }
});

dojo.declare("gnr.widgets.PalettePane", gnr.widgets.gnrwdg, {
    contentKwargs: function(sourceNode, attributes) {
        var inattr = sourceNode.getInheritedAttributes();
        var groupCode = inattr.groupCode;
        attributes.nodeId = attributes.nodeId || 'palette_' + attributes.paletteCode;
        attributes._class = attributes._class || "basePalette";
        if (groupCode) {
            attributes.groupCode = groupCode;
            attributes.pageName = attributes.paletteCode;
        }
        return attributes;
    },

    defaultDatapath:function(attributes) {
        return  'gnr.palettes.' + attributes.paletteCode;
    },
    createContent:function(sourceNode, kw) {
        var paletteCode = objectPop(kw, 'paletteCode');
        var contentWidget = objectPop(kw,'contentWidget') || 'ContentPane';
        var groupCode = objectPop(kw, 'groupCode');
        if (groupCode) {
            var pane = sourceNode._('ContentPane', objectUpdate({overflow:'hidden'},objectExtract(kw, 'title,pageName')))._(contentWidget, objectUpdate({'detachable':true}, kw));
            var controller_kw = {'script':"SET gnr.palettes._groups.pagename." + groupCode + " = paletteCode;",
                'paletteCode':paletteCode};
            controller_kw['subscribe_show_palette_' + paletteCode] = true;
            pane._('dataController', controller_kw);
            return pane;
        } else {
            var palette_kwargs = objectExtract(kw, 'title,dockTo,top,left,right,bottom,maxable,height,width,maxable,resizable');
            palette_kwargs.dockButton = objectPop(kw,'dockButton') || objectExtract(kw,'dockButton_*');
            palette_kwargs['nodeId'] = paletteCode + '_floating';
            palette_kwargs['title'] = palette_kwargs['title'] || 'Palette ' + paletteCode;
            objectUpdate(palette_kwargs, objectExtract(kw, 'palette_*'));
            palette_kwargs['subscribe_'+paletteCode+'_show'] = function(){
                this.widget.show();
                this.widget.bringToTop();
            };
            palette_kwargs.selfsubscribe_showing = function() {
                genro.publish('palette_' + paletteCode + '_showing');
            };
            palette_kwargs.selfsubscribe_hiding = function() {
                genro.publish('palette_' + paletteCode + '_hiding');
            };
            var floating = sourceNode._('palette', palette_kwargs);
            return floating._(contentWidget, kw);
        }
    }
});

dojo.declare("gnr.widgets.FramePane", gnr.widgets.gnrwdg, {
    createContent:function(sourceNode, kw,children) {
        var node;
        var frameCode = kw.frameCode;
        genro.assert(frameCode,'Missing frameCode');
        if(frameCode.indexOf('#')>=0){
            kw.frameCode = frameCode = frameCode.replace('#',sourceNode.getStringId()); 
        }
        var frameId = frameCode+'_frame';
        genro.assert(!genro.nodeById(frameId),'existing frame');
        sourceNode.attr.nodeId = frameId;
        sourceNode._registerNodeId();
        objectPop(kw,'datapath');
        var rounded_corners = genro.dom.normalizedRoundedCorners(kw.rounded,objectExtract(kw,'rounded_*',true));
        var centerPars = objectExtract(kw,'center_*');
        var bc = sourceNode._('BorderContainer', kw);
        var slot,slotcontent,v,sidepane,sideKw;
        var sides= kw.design=='sidebar'? ['left','right','top','bottom']:['top','bottom','left','right'];
        var corners={'left':['top_left','bottom_left'],'right':['top_right','bottom_right'],'top':['top_left','top_right'],'bottom':['bottom_left','bottom_right']};
        children.walk(function(n){
            if(n.attr.frameTarget && !n.attr.nodeId){
                n.attr.nodeId = frameCode+'_target';
            }
        },'static');
        dojo.forEach(sides,function(side){
            slot = children.popNode(side);
            slotcontent = null;
            sidepane = null;
            if(slot){
               slotcontent = slot.getValue();
               node = slotcontent.popNode('#0');
               if(slot.attr.tag=='autoslot'){
                    objectPop(slot.attr,'tag');
               }
            }else{
                node = children.popNode('#side='+side);
            }
            if(node){                 
                node.attr['frameCode'] = frameCode;
                sideKw = slot?objectUpdate(slot.attr,{'region':side}):{'region':side};
                sideKw.splitter = sideKw.splitter || objectPop(node.attr,'splitter');
                objectPop(node.attr,'side');
                dojo.forEach(corners[side],function(c){
                    v=objectPop(rounded_corners,c);
                    if(v){
                        node.attr['rounded_'+c] = v;
                    }
                });
                node.attr['_childname'] = node.attr['_childname'] || side;
                sidepane = bc._('ContentPane',sideKw);
                sidepane.setItem('#id',node._value,node.attr);
            }
            if(sidepane && slotcontent && slotcontent.len()>0){
                dojo.forEach(slotcontent.getNodes(),function(n){
                    n.attr['frameCode'] = frameCode;
                    sidepane.setItem('#id',n._value,n.attr);
                });
            }
        });
        slot = children.popNode('center');
        var centerNode = slot? slot.getValue().getNode('#0'):children.popNode('#side=center');
        var center;
        var rounded={};
        var frameChild;
        frameChild = children.popNode('#_frame=true::B');
        while(frameChild){
            objectPop(frameChild.attr,'_frame');
            bc.setItem(frameChild.label,frameChild._value,frameChild.attr);
            frameChild = children.popNode('#_frame=true::B');
        }
        
        for(var k in rounded_corners){
            rounded['rounded_'+k]=rounded_corners[k];
        }
        if(centerNode){
            objectPop(centerNode.attr,'side');
            centerNode.attr['region'] = 'center';
            centerNode.attr['_childname'] = centerNode.attr['_childname'] || 'center';
            bc.setItem('center',centerNode._value,objectUpdate(rounded,centerNode.attr));
            center = centerNode._value;
        }else{
            centerPars['region'] = 'center';
            centerPars['_childname'] = centerPars['_childname'] || 'center';
            centerPars['widget'] = centerPars['widget'] || 'ContentPane';
            center = bc._(centerPars['widget'],'center',objectUpdate(rounded,centerPars));
        }
        return center;
    }
});


dojo.declare("gnr.widgets.BoxForm",gnr.widgets.gnrwdg, {
    createContent:function(sourceNode, kw,children) {
        var formId = objectPop(kw,'formId');
        var storeNode = children.popNode('store');
        kw._class =  (kw._class || '') + ' fh_content';
        var store;
        if(storeNode){
            store = this.createStoreFromStoreNode(storeNode);
        }else{
            var storekw = objectExtract(kw,'store_*');
            storekw.handler = storekw.handler || objectPop(kw,'store') || 'memory';
            var storeType = objectPop(kw,'storeType');
            var parentStore = objectPop(kw,'parentStore');
            storeType = storeType ||(parentStore?'Collection':'Item');
            store = new gnr.formstores[storeType](storekw,{});
        }
        var controllerPath = objectPop(kw, 'controllerPath') || '#WORKSPACE.controller';
        var pkeyPath = objectPop(kw,'pkeyPath') || '#WORKSPACE.pkey';
        var formDatapath = objectPop(kw, 'formDatapath');
        return sourceNode._('div',objectUpdate({controllerPath:controllerPath,formDatapath:formDatapath,
                                                     pkeyPath:pkeyPath,formId:formId,form_store:store,_workspace:true},kw));
    },
    createStoreFromStoreNode:function(storeNode){
        var storeContent = storeNode.getValue();
        var action,callbacks;
        storeNode._value = null;
        var handlers = {};
        if(storeContent){
            storeContent.forEach(function(n){
                action = objectPop(n.attr,'action');
                if(action){
                    objectPop(n.attr,'tag');
                    handlers[action] = n.attr;
                    callbacks = n.getValue();
                    if(callbacks){
                        handlers[action]['callbacks'] = callbacks;
                    }
                }
            });
        }        
        var kw = storeNode.attr;
        var storeType = objectPop(kw,'storeType');
        storeType = storeType ||(kw.parentStore?'Collection':'Item');
        return new gnr.formstores[storeType](kw,handlers);
    }
});

dojo.declare("gnr.widgets.FrameForm", gnr.widgets.gnrwdg, {
    createContent:function(sourceNode, kw,children) {
        var formId = objectPop(kw,'formId');
        var storeNode = children.popNode('store');
        var contentNode = children.getNode('center');
        genro.assert(contentNode,'missing contentNode:  attach to form.center a layout widget');
        if(contentNode.attr.tag=='autoslot'){
            contentNode = children.getNode('center.#0');
            genro.assert(contentNode,'missing contentNode:  attach to form.center a layout widget');
        }
        contentNode.attr['_class'] =  (contentNode.attr['_class'] || '') + ' fh_content';
        var store = this.createStore(storeNode);
        var frameCode = kw.frameCode;
        formId = formId || frameCode+'_form';
        var frame = sourceNode._('FramePane',objectUpdate({controllerPath:'.controller',formDatapath:'.record',
                                                            pkeyPath:'.pkey',formId:formId,form_store:store},kw));        
        return frame;
    },
    createStore:function(storeNode){
        var storeContent = storeNode.getValue();
        var action,callbacks;
        storeNode._value = null;
        var handlers = {};
        if(storeContent){
            storeContent.forEach(function(n){
                action = objectPop(n.attr,'action');
                if(action){
                    objectPop(n.attr,'tag');
                    handlers[action] = n.attr;
                    callbacks = n.getValue();
                    if(callbacks){
                        handlers[action]['callbacks'] = callbacks;
                    }
                }
            });
        }        
        var kw = storeNode.attr;
        var storeType = objectPop(kw,'storeType');
        storeType = storeType ||(kw.parentStore?'Collection':'Item');
        return new gnr.formstores[storeType](kw,handlers);
    }
});

dojo.declare("gnr.widgets.PaletteMap", gnr.widgets.gnrwdg, {
    contentKwargs:function(sourceNode, attributes){
        return attributes;
    },
    createContent:function(sourceNode, kw,children) {
        var paletteCode=kw.paletteCode;
        kw.frameCode = paletteCode;
        kw['contentWidget'] = 'FramePane';
        var mapKw = objectExtract(kw,'map_*',false,true)
        var pane = sourceNode._('PalettePane',kw);
        var centerMarker = objectPop(kw,'centerMarker',true);
        if(centerMarker){
            mapKw.centerMarker = true;
        }
       //if(kw.searchOn){
       //    //var bar = pane._('SlotBar',{'side':'top',slots:'fbpars,*',searchOn:objectPop(kw,'searchOn'),toolbar:true});
       //    //var fb = genro.dev.formbuilder(bar._('div','fbpars',{}),{border_spacing:'1px',width:'100%',margin_bottom:'12px'});
       //   // _('horizontalSlider',{'value':'^.zoom'});
       //   // 
       //   //         fb.horizontalSlider(value='^.zoom',lbl='Zoom',minimum=4,maximum=21,width='150px',discreteValues=18)
       //
       //}
        
        var mapNode = pane._('GoogleMap',objectUpdate({'height':'100%',map_type:'roadmap'},mapKw)).getParentNode();
        
        var paletteNode = pane.getParentNode();
    
        paletteNode.addMapMarker = function(marker_name,marker){
            var kw={title:marker_name,draggable:true}
            mapNode.gnr.setMarker(mapNode,marker_name,marker,kw)
        };
        paletteNode.removeMapMarker = this.removeMapMarker;
        return pane;
    }
});

dojo.declare("gnr.widgets.PaletteGrid", gnr.widgets.gnrwdg, {
    contentKwargs:function(sourceNode, attributes){
        var gridId = attributes.gridId || attributes.paletteCode+'_grid';
        attributes['frameCode'] = attributes.paletteCode;
        return attributes;
    },
    createContent:function(sourceNode, kw,children) {
        kw['contentWidget'] = 'FramePane';
        kw['center_overflow'] = 'hidden';
        var pane = sourceNode._('PalettePane',kw);
        if(kw.viewResource){
            return this.createContent_remoteTableHandler(pane,sourceNode,kw);
        }else{
            return this.createContent_paletteGrid(pane,sourceNode,kw);
        }
    },

    createContent_remoteTableHandler:function(pane,sourceNode,kw){
        var paletteCode=kw.paletteCode;
        kw['grid_onDrag'] = "dragValues['"+paletteCode+"']=dragValues.gridrow.rowset;"
        kw['nodeId'] = kw.paletteCode
        return pane._('ContentPane','remoteTH',{
            overflow:'hidden',
            remote:'th_remoteTableHandler',
            remote_py_requires:'th/th:TableHandler',
            remote_thkwargs:kw
        });
    },

    createContent_paletteGrid:function(pane,sourceNode,kw){
        var gridId = objectPop(kw, 'gridId') || frameCode+'_grid';
        var storepath = objectPop(kw, 'storepath');
        var structpath = objectPop(kw, 'structpath');
        var store = objectPop(kw, 'store');
        var _newGrid = objectPop(kw,'_newGrid',true);
        var frameCode = kw.frameCode;
        var paletteCode=kw.paletteCode;
        structpath = structpath? sourceNode.absDatapath(structpath):'.struct';
        var gridKwargs = {'nodeId':gridId,'datapath':'.grid',
                           'table':objectPop(kw,'table'),
                           'configurable':true,
                           'structpath': structpath,
                           'frameCode':frameCode,
                           'autoWidth':false,
                           'store':store,
                           'relativeWorkspace':true};   
        gridKwargs.onDrag = function(dragValues, dragInfo) {
            if (dragInfo.dragmode == 'row') {
                dragValues[paletteCode] = dragValues.gridrow.rowset;
            }
        };     
        gridKwargs.draggable_row=true;
        objectUpdate(gridKwargs, objectExtract(kw, 'grid_*'));
        if(kw.searchOn){
            pane._('SlotBar',{'side':'top',slots:'*,searchOn',searchOn:objectPop(kw,'searchOn'),toolbar:true});
        }
        pane._(_newGrid?'newIncludedView':'includedview', 'grid',gridKwargs);
        var gridnode = pane.getNode('grid');
        return pane;
    }

});

dojo.declare("gnr.widgets.TreeFrame", gnr.widgets.gnrwdg, {
    getRoot:function(sourceNode,kw){
        return sourceNode._('FramePane',kw);
    },
    subtags : {column:true},
    createContent:function(sourceNode, kw,children,subTagItems) {
        
        kw.frameCode = kw.frameCode || kw.paletteCode;
        var frameCode = kw.frameCode;
        var editable = objectPop(kw, 'editable');
        var treeId = objectPop(kw, 'treeId') || frameCode + '_tree';
        var storepath = objectPop(kw, 'storepath') || '.store';
        var draggableFolders = objectPop(kw,'draggableFolders');
        var infoPanel = normalizeKwargs(kw,'infoPanel');
        var default_onDrag =  function(dragValues, dragInfo, treeItem) {
            if (treeItem.attr.child_count && treeItem.attr.child_count > 0 && !draggableFolders) {
                return false;
            }
            dragValues['text/plain'] = treeItem.attr.caption;
            dragValues[frameCode] = treeItem.attr;
        };
        var tree_kwargs = {_class:'fieldsTree', hideValues:true,
                            margin:'6px',nodeId:treeId,draggable:true,
                            'frameCode':frameCode,onDrag:default_onDrag,
                            storepath:storepath,labelAttribute:'caption',
                        };
        objectUpdate(tree_kwargs, objectExtract(kw, 'tree_*'));
        var searchOn = objectPop(kw, 'searchOn');
        var pane = this.getRoot(sourceNode,kw);
        var bc;
        if (searchOn) {
            pane._('SlotBar',{'side':'top',slots:'*,searchOn',searchOn:true,toolbar:true});
        }
        if (editable) {
            var bagNodeEditorId = treeId + '_editbagbox';
            var origin = stringStartsWith(storepath,'*S')?'*S':null
            tree_kwargs.selfsubscribe_onSelected = function(kw){                
                genro.publish(bagNodeEditorId+'_currentPath',kw.item.getFullpath(null,origin!='*S'?genro._data:null))
            }
            bc = pane._('BorderContainer',{'side':'center'});
            var bottom = bc._('ContentPane', {'region':'bottom',height:'30%',
                splitter:true,overflow:'hidden'});
            bottom._('BagNodeEditor', {nodeId:bagNodeEditorId,datapath:'.bagNodeEditor',origin:origin});
            pane = bc._('ContentPane',{'region':'center'});
        }else if(infoPanel){
            bc = pane._('BorderContainer',{'side':'center'});
            infoPanel.region = infoPanel.region || 'right';
            if(['left','right'].indexOf(infoPanel.region)>=0){
                infoPanel.width = infoPanel.width || '300px';
            }
            infoPanel.remote = objectPop(infoPanel,'_');
            bc._('ContentPane',infoPanel);
            pane = bc._('ContentPane',{'region':'center'});
        }
        if(subTagItems['column'] && subTagItems['column'].len()){
            var tg = pane._('treegrid',tree_kwargs);
            subTagItems['column'].forEach(function(n){
                tg._('column',null,n.attr);
            });
        }else{
            pane._('tree', tree_kwargs);
        }
        
        return pane;
    }
});

dojo.declare("gnr.widgets.PaletteTree", gnr.widgets.TreeFrame, {
    getRoot:function(sourceNode,kw){
        kw['contentWidget'] = 'FramePane';
        return sourceNode._('PalettePane',kw);
    }
});

dojo.declare("gnr.widgets.PaletteImporter", gnr.widgets.gnrwdg, {
    createContent:function(sourceNode, kw) {
        var frameCode = kw.frameCode = kw.paletteCode;
        var table = objectPop(kw, 'table');
        var gnrwdg = sourceNode.gnrwdg;
        gnrwdg.table = table;
        gnrwdg.match_values = objectPop(kw,'match_values');
        var uploadPath = objectPop(kw,'uploadPath');
        var filename = objectPop(kw,'filename');
        var maxsize = objectPop(kw,'maxsize');
        gnrwdg.filename = filename || frameCode+'latest';
        gnrwdg.uploadPath = uploadPath;
        kw.height = kw.height || '400px';
        kw.width = kw.width || '650px';
        sourceNode.attr.nodeId = frameCode;
        sourceNode._registerNodeId();
        gnrwdg.matchColumns = objectPop(kw,'matchColumns');
        gnrwdg.importButtonKw = objectExtract(kw,'importButton_*');
        gnrwdg.importMethod = objectPop(kw,'rpcmethod');
        var errorCb = objectPop(kw,'errorCb');
        gnrwdg.errorCb = errorCb? funcCreate(errorCb,'error',sourceNode):null;
        gnrwdg.batchParameters = objectExtract(kw,'batch_*');
        gnrwdg.uploaderId = sourceNode.attr.nodeId +'_uploader';
        gnrwdg.constant_kwargs = objectExtract(kw,'constant_*',false,true);
        gnrwdg.sql_mode = objectPop(kw,'sql_mode');
        var palette = sourceNode._('PalettePane',kw);
        var bc = palette._('BorderContainer',{_lazyBuild:true});
        var slots = '2,prevtitle,importselector,*,limit,5';
        var limit = objectPop(kw,'previewLimit') || 20;
        var filetype = objectPop(kw,'filetype');
        var dropMessage = objectPop(kw,'dropMessage') || '!!Drop import file here';
        if(!gnrwdg.matchColumns){
            gnrwdg.matchGrid(bc);
        }
        var frame = bc._('FramePane',{frameCode:frameCode,region:'center',
                                     _class:'pbl_roundedGroup',margin:'2px'});
        var bar = frame._('SlotBar',{'side':'top',slots:slots,searchOn:true,_class:'pbl_roundedGroupLabel'});
        bar._('div','prevtitle',{innerHTML:"==_current_title || 'Import'",_current_title:'^.current_title',color:'#666'});
        if(!filetype){
            bar._('filteringSelect','importselector',{value:'^.filetype',width:'4em',values:'excel,csv,tab,xml',margin_top:'2px'});
        }else{
            bar._('div','importseletor')
        }
        bar._('div','limit',{innerHTML:_T('The lines in preview are limited to')+' '+limit,font_style:'italic',font_size:'.8em'});

        var dropAreaKw = {};
        if(kw.importerStructure){
            dropAreaKw.rpc_importerStructure = objectPop(kw,'importerStructure');
        }
        dropAreaKw.nodeId = frameCode+'_uploader';
        dropAreaKw.onUploadingCb = function(dropInfo,data){
            var uploaderNode = genro.nodeById(gnrwdg.uploaderId);
            uploaderNode.setRelativeData('.current_title',data.name);
        };
        dropAreaKw.rpc_limit = limit;
        dropAreaKw.rpc_table = table;
        dropAreaKw.rpc_filetype = filetype|| '=.filetype';
        dropAreaKw.rpc_collection_path = '=.collection_path';
        dropAreaKw.rpc_row_tag= '=.row_tag';

        objectUpdate(dropAreaKw,objectExtract(kw,'drop_*',false,true));
        dropAreaKw.onResult = function(result){
                                if(result.currentTarget.responseText){
                                    gnrwdg.onImportCheck(new gnr.GnrBag(result.currentTarget.responseText));
                                }                            
                           }
        dropAreaKw.filename = gnrwdg.filename;
        dropAreaKw.uploadPath = gnrwdg.uploadPath;
        var sc = bc._('StackContainer',{region:'bottom',height:'30px',selected:'^.import_page_status',
                                            border_top:'1px solid silver',background:'white'});
        sc._('ContentPane',{overflow:'hidden'})._('DropUploader','msgslot',
                                    objectUpdate({label:_T(dropMessage),
                                                  font_size:'1.2em',position:'absolute',top:0,left:'3px',right:'3px',bottom:0,
                                                  color:'#666',text_align:'center',
                                                  onUploadedMethod:'utils.tableImporterCheck',
                                                  _class:'importerPaletteDropUploaderBox',
                                                  cursor:'pointer',
                                                  nodeId:gnrwdg.uploaderId
                                                 },dropAreaKw))
        var confirmPane = sc._('ContentPane',{});
        var footerbar = confirmPane._('slotBar',{slots:'5,resetButton,*,importButton,5',margin_top:'5px'});
        footerbar._('slotButton','resetButton',{label:'Clear',width:'8em',font_size:'1em',padding:'2px',
                                            action:function(){gnrwdg.resetImporter();}});
        var importButtonKw = objectUpdate({label:'Import',width:'8em',font_size:'1em',padding:'2px',
                                        imported_file_path:'=.imported_file_path',
                                        match:'=.match',
                                        action:function(){
                                            if(objectNotEmpty(gnrwdg.batchParameters)){
                                                genro.publish('table_script_run',this.evaluateOnNode(gnrwdg.batchParameters));
                                                gnrwdg.resetImporter();
                                                genro.wdgById(frameCode+'_floating').hide();
                                            }else{
                                                gnrwdg.importDo(this);
                                            }
                                    },disabled:'^.imported_file_path?=!#v'},gnrwdg.importButtonKw)
        footerbar._('slotButton','importButton',importButtonKw);
        var qg = frame._('borderContainer',{'side':'center'})._('quickGrid', {value:'^.importing_data',region:'center'});
        gnrwdg.gridNode = qg.getParentNode();
        var bcnode = bc.getParentNode();
        gnrwdg.rootNode = bcnode;

        sourceNode.subscribe('onResult',function(kw){
            if(kw instanceof gnr.GnrBag){
                kw = {
                    error:kw.pop('error'),
                    message:kw.pop('message'),
                    closeImporter:kw.pop('closeImporter')
                }
            }
            if(kw.error){
                if (gnrwdg.errorCb){
                    gnrwdg.errorCb(kw.error);
                }else{
                    genro.dlg.floatingMessage(bcnode,{message:kw.error,messageType:'error'});
                }
            }
            else{
                this.gnrwdg.resetImporter();
                var closeCb = function(){
                    genro.wdgById(frameCode+'_floating').hide()
                }
                if(kw.message){
                    genro.dlg.floatingMessage(bcnode,{message:kw.message,onClosedCb:kw.closeImporter?closeCb:null})
                }else if(kw.closeImporter){
                    closeCb();
                }
            }
        });
        return bc;
    },


    gnrwdg_matchGrid:function(bc){
        var gnrwdg = this;
        var frame = bc._('FramePane',{frameCode:this.uploaderId+'_matchframe',_anchor:true,
                                        region:'left',_class:'pbl_roundedGroup',margin:'2px',
                                        drawer:'close',width:'320px',splitter:true})
        bar = frame._('slotBar',{slots:'2,matchtitle,*',side:'top',_class:'pbl_roundedGroupLabel'});
        bar._('div','matchtitle',{innerHTML:'Match columns'});
       //bar._('div','lbl_action',{innerHTML:'Action'});
       //bar._('filteringSelect','action_filter',{values:'insert,update',
       //                        value:'^.import_action',width:'6em',default_value:'insert'})
        bar = frame._('slotBar',{slots:'2,fbbottom,*',side:'bottom',_class:'slotbar_dialog_footer'});

        var fb = genro.dev.formbuilder(bar._('div','fbbottom'),3,{border_spacing:'1px'});
        fb.addField('filteringSelect',{value:'^.import_method',width:'7em',
                                        lbl_text_align:'right',
                                        lbl_class:'gnrfieldlabel',
                                        lbl:_T('Method'),
                                        values:'^.methodlist',
                                        lbl_hidden:'^.methodlist?=!#v',
                                        hidden:'^.methodlist?=!#v',
                                        parentForm:false});
        fb.addField('filteringSelect',{value:'^.import_mode',width:'7em',
                    lbl_text_align:'right',
                    lbl_class:'gnrfieldlabel',
                    lbl:_T('Mode'),
                    lbl_hidden:'^.import_modes?=!#v',
                    hidden:'^.import_modes?=!#v',
                    values:'^.import_modes',
                    parentForm:false});

        if (this.table && !this.sql_mode){
            fb.addField('checkbox',{value:'^.sql_mode',
                                label:_T('SQL Mode'),parentForm:false});   
        }
        var grid = frame._('BorderContainer',{'side':'center',overflow:'hidden'})._('quickGrid',{value:'^.match',_class:'noselect',region:'center'});
        grid.getParentNode().importer_gnrwdg = this;
        var onclick = "this.getParentNode().importer_gnrwdg.onCheckedMatch(this,kw);"
        var editdestpars = true;
        if(this.match_values){
            editdestpars = {tag:'combobox',values:this.match_values,validate_onAccept:"if(value){this.setRelativeData('.do_import',true)}"};
        }
        grid._('column',{name:'Key',field:'is_key',width:'2em',dtype:'B',
                        hidden:'^#ANCHOR.import_mode?=#v!="update_only"',
                        checkBoxColumn:{radioButton:true},
                        cellStyles:'border-bottom:1px solid lightgray;background:white;'})

        grid._('column',{name:'Source Column',field:'source_field',width:'10em',
                cellStyles:'background:#666;color:whitesmoke;text-align:right; border-left:0px;border-bottom:1px solid whitesmoke;'})
        grid._('column',{name:'Dest.Column',field:'dest_field',cellStyles:'border-bottom:1px solid lightgray;background:white;',edit:editdestpars,width:'10em'})
        if(!this.table){
            grid._('column',{name:'Type',field:'dtype',cellStyles:'border-bottom:1px solid lightgray;background:white;',
                        edit:{values:'T:Text,L:Integer,N:Decimal,D:Date,B:Boolean,H:Time,P:Image',tag:'filteringSelect'},width:'7em'})
        }
        grid._('column',{name:' ',field:'do_import',width:'2em',dtype:'B',
                        format_onclick:onclick,cellStyles:'border-bottom:1px solid lightgray;background:white;'})
    
    },

    gnrwdg_resetImporter:function(){
        var uploaderNode = genro.nodeById(this.uploaderId);
        uploaderNode.setRelativeData('.current_title',null);
        uploaderNode.setRelativeData('.methodlist','');
        uploaderNode.setRelativeData('.import_modes','');
        uploaderNode.setRelativeData('.import_mode','');
        uploaderNode.setRelativeData('.importing_data',null);
        uploaderNode.setRelativeData('.file_columns',null);
        uploaderNode.setRelativeData('.match',null);
        uploaderNode.setRelativeData('.imported_file_path',null);
        uploaderNode.setRelativeData('.import_page_status',0);
        this.gridNode.gnrwdg.setColumns(new gnr.GnrBag());
    },

    gnrwdg_onImportCheck:function(data){
        var errors = data.getItem('errors');
        if(errors){
            genro.dlg.floatingMessage(this.rootNode,{message:errors,messageType:'error'});
            return;
        }
        var columns = data.getItem('columns');
        var match_data = data.getItem('match_data');
        var warning = false;
        if(this.matchColumns && this.matchColumns!='*'){
            var colkeys = columns.keys();
            var matchColumns = this.matchColumns.split(',');
            if(matchColumns.length!=colkeys.length || matchColumns.some(function(n,idx){return n!=colkeys[idx]})){
                genro.dlg.floatingMessage(this.rootNode,{message:_T('Columns mismatch'),messageType:'error'})
                return;
            }
        }
        this.gridNode.gnrwdg.setColumns(columns);
        this.gridNode.gnrwdg.guessColumns = false;
        var uploaderNode = genro.nodeById(this.uploaderId);
        uploaderNode.setRelativeData('.methodlist',data.getItem('methodlist'));
        uploaderNode.setRelativeData('.import_modes',data.getItem('import_modes'));
        uploaderNode.setRelativeData('.import_mode',data.getItem('import_mode'));
        uploaderNode.setRelativeData('.importing_data',data.getItem('rows'));
        uploaderNode.setRelativeData('.file_columns',columns);
        uploaderNode.setRelativeData('.match',match_data);
        uploaderNode.setRelativeData('.imported_file_path',data.getItem('imported_file_path'));
        uploaderNode.setRelativeData('.import_page_status',1);
    },

    gnrwdg_onCheckedMatch:function(matchGrid,kw){
        var p = '#'+kw.rowIndex+'.do_import'; 
        var s = matchGrid.widget.collectionStore().getData();
        s.setItem(p,!s.getItem(p));
        var previewStructCells = this.gridNode.getRelativeData('#WORKSPACE.struct.#0.#0')
        var importfields = s.values().forEach(function(v){
            var nprev = previewStructCells.getNode(v.getItem('source_field'));
            if(v.getItem('do_import')){
                delete nprev.attr.hidden;
            }else{
                nprev.attr.hidden = true;
            }
        });
        this.gridNode.setRelativeData('#WORKSPACE.struct?_updated',genro.getCounter());
    },
    gnrwdg_importDo:function(buttonNode){
        var match_index;
        var match = buttonNode.getRelativeData('.match');
        if (match && match.len()){
            match_index = {};
            match.values().forEach(function(v){
                if(v && v.getItem('do_import')){
                    match_index[v.getItem('source_field')] = v.getItem('dest_field') || v.getItem('source_field');
                    if(v.getItem('is_key')){
                        match_index._updater_keyfield = v.getItem('dest_field');
                    }
                }
            })
        }
        var that = this;
        genro.lockScreen(true,'import_data',{thermo:true});
        var importerKw = {table:this.table,file_path:'=.imported_file_path',
            match_index:match_index,
            import_method:'=.import_method',
            import_mode:'=.import_mode',
            filetype:'=.filetype',
            sql_mode:this.sql_mode || '=.sql_mode',
            timeout:3600000,
            _sourceNode:buttonNode};
        if(this.constant_kwargs){
            objectUpdate(importerKw,this.constant_kwargs);
        }

        genro.serverCall(this.importMethod || 'utils.tableImporterRun',importerKw,function(result){
            
            genro.dlg.floatingMessage(that.rootNode,{message:_T('Import finished')});
            if(result && result.warnings){
                genro.dlg.floatingMessage(that.rootNode,{message:result.warnings});

            }
            that.resetImporter();
            genro.lockScreen(false,'import_data');
        });
    }
});



dojo.declare("gnr.widgets.VideoPickerPalette", gnr.widgets.gnrwdg, {
    createContent:function(sourceNode, kw,children) {
        var paletteKw = objectExtract(kw,'palette_*')
        var paletteCode = paletteKw.paletteCode = objectPop(kw,'paletteCode') || 'capturePicker';
        paletteKw.height = paletteKw.height || '700px';
        paletteKw.width = paletteKw.width || '420px';
        paletteKw.dockButton = 'dockButton' in paletteKw? paletteKw.dockButton:true;
        paletteKw.selfsubscribe_showing = function(){
            genro.publish(paletteCode+'_video'+'_startCapture');
        }
        var palette = sourceNode._('PalettePane',paletteKw);
        var bc = palette._('BorderContainer')
        var top = bc._('framePane',{frameCode:paletteCode+'_cam',region:'top',height:'350px',splitter:true});
        var bar = top._('SlotBar',{'side':'bottom',slots:'*,zoomSlider,5,snap,5',toolbar:true});
        bar._('horizontalSlider','zoomSlider',{value:'^.currentZoom','default':0.3,minimum:0.3, maximum:1,intermediateChanges:true, width:'15em',margin_top:'2px'});
        bar._('slotButton','snap',{label:'Take picture',iconClass:'iconbox photo',action:function(){
            genro.publish(paletteCode+'_video'+'_takePicture');
        }})
        top._('video',{autoplay:true,height:'300px',width:'400px',margin:'10px',nodeId:paletteCode+'_video',
                        selfsubscribe_takePicture:function(){
                            var box = genro.nodeById(paletteCode+'_preview');
                            var c = box._('canvas',{height:'300px',width:'400px',display:'inline-block',margin:'5px',draggable:true,
                                            onDrag:function(dragValues, dragInfo){
                                                dragValues['dataUrl'] = dragInfo.sourceNode.domNode.toDataURL('image/png');
                                            }})
                            c.getParentNode().takePhoto(this);
                        },selfsubscribe_startCapture:function(){this.startCapture({video:true})}});
        var center = bc._('FramePane',{frameCode:paletteCode+'_viewer',region:'center'});

        center._('div','box',{position:'absolute',overflow:'auto',top:'2px',left:'2px',right:'2px',bottom:'2px',
                                                                    nodeId:paletteCode+'_preview',zoom:'^.currentZoom'});
        return palette;
    }    
});


dojo.declare("gnr.widgets.MultiValueEditor", gnr.widgets.gnrwdg, {
    createContent:function(sourceNode, kw) {
        var gnrwdg = sourceNode.gnrwdg;
        gnrwdg.editNodeValue = objectPop(kw,'editNodeValue');
        gnrwdg.origin = objectPop(kw,'origin');
        sourceNode.attr.exclude = objectPop(kw,'exclude');
        sourceNode.attr.value = objectPop(kw,'value');
        var grid_kwargs = objectExtract(kw,'grid_*');
        var tools = objectPop(kw,'tools');
        var tools_kw = objectExtract(kw,'tools_*');
        var readOnly = objectPop(kw,'readOnly');

        if(tools==undefined && !readOnly){
            tools = 'delrow,addrow';
        }
        gnrwdg.exclude = sourceNode.currentFromDatasource(sourceNode.attr.exclude);

        var container = sourceNode._('BorderContainer',objectUpdate({
            selfsubscribe_setSource:function(source){
                gnrwdg.setSource(source);
            }
        },kw));
        gnrwdg.containerNode = container.getParentNode();
        var grid = container._('ContentPane',{region:'center',overflow:'hidden'})._('quickGrid',objectUpdate({value:'^#WORKSPACE.value',_workspace:true,
                                            _class:'multiValueEditor noheader',storeInForm:true,
                                            border:'1px solid #efefef',
                                                selfsubscribe_addrow:function(addkw){
                                                    var grid = this.widget;
                                                    setTimeout(function(){
                                                        gnrwdg.addEditorRow(grid,addkw);
                                                    },500)
                                                    //
                                                }
                                            },grid_kwargs));
        grid._('column',{name:'Key',field:'attribute_key',width:'15em',cellStyles:'background:#BBB;color:#333;border-bottom:1px solid white;font-weight:bold;'})
        grid._('column',{name:'Value',field:'attribute_value',edit:!readOnly,width:'100%',cellStyles:'border-bottom:1px solid lightgray;'})
        if(tools){
            var t = grid._('tools',objectUpdate({tools:tools,
                                          custom_tools:{addrow:{content_class:'iconbox add_row',ask:{title:'New Line',
                                                fields:[{name:'attribute_key',lbl:'Key',validate_notnull:true},
                                                        {name:'dtype',lbl:'Datatype',
                                                        values:'T:Text,B:Boolean,L:Integer,N:Decimal,D:Date,H:Time',
                                                        wdg:'filteringSelect',default_value:'T'},
                                                        {name:'attribute_value',lbl:'Value'}]
                                                }
                                    }
            }},tools_kw))

        }
        gnrwdg.gridNode = grid.getParentNode();
        if(sourceNode.attr.value){
            gnrwdg.setSource(sourceNode.attr.value);
        }
        var dc = gnrwdg.gridNode._('dataController',{script:'this._onGridChangedData(data,_triggerpars)',data:'^#WORKSPACE.value'})
        dc.getParentNode()._onGridChangedData = function(data,_triggerpars){
            gnrwdg.tempBagTrigger(data,_triggerpars)
        }
        return grid
    },

    gnrwdg_addEditorRow:function(grid,kw){
        var key = kw.attribute_key;
        var value = kw.attribute_value;

        var dtype = kw.dtype;
        if(!key){
            genro.dlg.floatingMessage(this.containerNode,{messageType:'error',message:'Missing key'})
            return;
        }
        if(this.exclude && this.exclude.split(',').indexOf(key)>=0){
            genro.dlg.floatingMessage(this.containerNode,{messageType:'error',message:'You cannot add this key'})
            return;
        }
        grid.addRows([{'attribute_key':key,'attribute_value':value}],null,null,function(firstRow){
            var valueNode = firstRow._value.getNode('attribute_value');
            valueNode.attr.wdg_dtype = dtype || 'T';
            if(!isNullOrBlank(value)){
                valueNode.setValue(value); //it must not be evauluated
                return false;
            }
        });
        
    },

    gnrwdg_setExclude:function(value){
        this.exclude = value;
        this.setTempStore();
    },

    gnrwdg_setValue:function(value,kw,reason){
        if(reason=='child'){
            return;
        }
        this.setTempStore();
    },

    gnrwdg_setSource:function(value){
        if(typeof(value)!='string'){
            this.source_item = value;
        }else{
            if(this.origin=='*S'){
                this.source_root =genro.src._main;
                this.valuepath = value;
            }else{
                this.source_root = genro._data;
                this.valuepath = this.sourceNode.absDatapath(value);
            }
        }
        this.setTempStore();
    },
    
    gnrwdg_getSource:function(){
        if(this.source_item){
            return this.source_item;
        }
        var result = isNullOrBlank(this.valuepath)?this.source_root:this.source_root.getItem(this.valuepath,null,'static');
        if(!result && this.valuepath){
            result = new gnr.GnrBag();
            this.source_root.setItem(this.valuepath,result,null,{doTrigger:false});
        }
        return result;
    },

    gnrwdg_setTempStore:function(){
        var exclude = (this.exclude || '').split(',');
        var addRow = function(where,key,value,dtype){
            if(exclude.indexOf(key)>=0){
                return;
            }
            var r = new gnr.GnrBag();
            var keyattr,rowattr;
            if(value instanceof gnr.GnrBag){
                value = '*bag*';
            }
            if(key=='*value'){
                keyattr = {editDisabled:true};
                rowattr = {_protect_delete:true};
            }
            r.setItem('attribute_key',key,keyattr);
            var value_attr = {wdg_dtype:dtype || guessDtype(value) || 'T'};
            if(value_attr.wdg_dtype=='X'){
                value_attr['editDisabled'] = true;
            }
            r.setItem('attribute_value',value,value_attr);
            where.setItem('#id',r,rowattr);
        }
        var source = this.getSource();
        var result = new gnr.GnrBag();
        if(source instanceof gnr.GnrBagNode){
            if(this.editNodeValue){
                addRow(result,'*value', source.getValue('static'));
            }
            source = source.attr;
        }
        if(source instanceof gnr.GnrBag){
            source.forEach(function(n){
                addRow(result,n.label,n.getValue(),n.attr.dtype);
            });
        }else{
            for(var k in source){
                addRow(result,k,source[k]);
            }
        }
        this.gridNode.setRelativeData('#WORKSPACE.value',result,null,null,'loadData');
    },

    gnrwdg_tempBagTrigger:function(data,_triggerpars){
        var trigger_kwargs = _triggerpars.kw;
        if(trigger_kwargs.reason=='initStore' || trigger_kwargs.reason=='loadData'){
            return;
        }
        var evt = trigger_kwargs.evt;
        var k,v,vn;
        var source = this.getSource();
        if(evt=='upd'){
            var r = trigger_kwargs.node.getParentBag()
            k = r.getItem('attribute_key');
            vn = r.getNode('attribute_value');
            if(!vn){
                //parentTrigger is loading the whole store
                return;
            }
            v = vn.getValue();
            if(vn.attr.dtype=='AR'){
                v = v.split(',');
            }
            if(source instanceof gnr.GnrBagNode){
                if(k=='*value'){
                    source.setValue(v,true);
                }else{
                    source.setAttribute(k,v,true);
                }
            }else{
                if(source instanceof gnr.GnrBag){
                    source.setItem(k,v,null,{lazySet:true});
                }else{
                    source[k] = v;
                }
                
            }
        }else if(evt=='del'){
            k = trigger_kwargs.node._value.getItem('attribute_key');
            if(source instanceof gnr.GnrBagNode){
                source.setAttribute(k,null);
            }else{
                if(source instanceof gnr.GnrBag){
                    source.popNode(k);
                }else{
                    objectPop(source,k);
                }
            }
        }
    }
});

dojo.declare("gnr.widgets.PaletteBagNodeEditor", gnr.widgets.gnrwdg, {
    createContent:function(sourceNode, kw) {
        var pane = sourceNode._('PalettePane', kw);
        var nodePath = objectPop(kw,'nodePath');
        var multiValuePars = objectExtract(kw,'origin,exclude')
        var bc = pane._('BorderContainer', {_class:'bagNodeEditor'});
        if(genro.isDeveloper){
            var bottom = bc._('ContentPane', {'region':'bottom',color:'#666',font_style:'italic'});
            bottom._('span', {'innerHTML':'Path : '});
            bottom._('span', {'innerHTML':nodePath,_class:'selectable'});
        }
        bc._('ContentPane',{region:'center',margin:'2px',overflow:'hidden'})._('MultiValueEditor',objectUpdate({value:nodePath+'?#node'},multiValuePars))
        return pane;
    }
});

dojo.declare("gnr.widgets.PaletteBagEditor", gnr.widgets.gnrwdg, {
    createContent:function(sourceNode, kw) {
        var palette_kw = objectExtract(kw,'paletteCode,groupCode,dockTo,title');
        objectUpdate(palette_kw,objectExtract(kw,'palette_*',null,true));
        palette_kw.palette_width = kw.palette_width || '500px';
        var pane = sourceNode._('PalettePane', palette_kw);
        pane._('FlatBagEditor',kw);
        return pane;
    }
});

dojo.declare("gnr.widgets.FlatBagEditor", gnr.widgets.gnrwdg, {
    createContent:function(sourceNode, kw) {
        var gnrwdg = sourceNode.gnrwdg;
        var path = objectPop(kw,'path');
        var toolskw = objectExtract(kw,'addrow,delrow');

        var multiValuePars = objectExtract(kw,'origin,exclude');
        var box_kw = objectUpdate({},objectExtract(kw,'box_*'));
        var bc = sourceNode._('BorderContainer',box_kw);
        var grid_region = objectPop(kw,'grid_region','left');
        var boxpars = {region:grid_region,_class:'noheader no_over',
                        margin:'2px',border:'1px solid #efefef',
                        splitter:true};
        if(grid_region=='left' || grid_region=='right'){
            boxpars.width = '30%';
        }else{
            boxpars.height = '50%';
        }
        var left = bc._('ContentPane',boxpars);
        var grid_attr = {value:'^'+path,datamode:'attr',
            selfDragRows:true,
            selfsubscribe_onSelectedRow:function(kw){
                  if(kw.idx>=0){
                      var n = this.widget.collectionStore().itemByIdx(kw.idx);
                      //gnrwdg.mveNode.gnrwdg.setSource(nodePath+'?#node');
                      gnrwdg.mveNode.gnrwdg.setSource(path+'.'+n.label+'?#node');
                  }
            },
             onCreated:function(){
                  var w = this.widget;
                  setTimeout(function(){
                      w.updateRowCount();
                  },1);
            }
        };
        objectUpdate(grid_attr,objectExtract(kw,'grid_*'));
        var g = left._('quickGrid','nodeListGrid',grid_attr);
        g._('column',{field:'field',name:'Cells',width:'100%'});
        var t = [];
        if(toolskw.delrow){
            t.push('delrow');
            if(toolskw.delrow===true){
                objectPop(toolskw,'delrow')
            }
        }       
        if(toolskw.addrow){
            t.push('addrow');
            if(toolskw.addrow===true){
                objectPop(toolskw,'addrow')
            }
        }
        if(t.length){
            g._('tools',{tools:t.join(','),
                    custom_tools:toolskw,title:_T('Rows')});
        }
        //multiValuePars.tools_position = 'BL';
        multiValuePars.tools_title = _T('Attributes');
        var mve = bc._('ContentPane',{region:'center',margin:'2px',overflow:'hidden'
                                        })._('MultiValueEditor','mve',multiValuePars);
        gnrwdg.mveNode = mve.getParentNode();
        return bc;
    }
});

dojo.declare("gnr.widgets.BagNodeEditor", gnr.widgets.gnrwdg, {
    createContent:function(sourceNode, kw) {
        var gnrwdg = sourceNode.gnrwdg;
        var nodeId = objectPop(kw, 'nodeId');
        var readOnly = objectPop(kw, 'readOnly', false);
        var showBreadcrumb = objectPop(kw, 'showBreadcrumb', true);
        var bc = sourceNode._('BorderContainer', {detachable:true,_class:'bagNodeEditor',nodeId:nodeId,
                                                    selfsubscribe_currentPath:function(nodePath){
                                                        gnrwdg.setCurrentPath(nodePath);
                                                    }
                                                    });
        if (showBreadcrumb) {
            var bottom = bc._('ContentPane', {'region':'bottom',color:'#666',font_style:'italic'});
            bottom._('span', {'innerHTML':'Path : '});
            bottom._('span', {'innerHTML':'^.currentEditedPath',_class:'selectable'});
        }
        var box = bc._('ContentPane', {'region':'center',_class:'formgrid',overflow:'hidden'});

        var mve = box._('MultiValueEditor','mve',{origin:kw.origin,editNodeValue:true})
        gnrwdg.mveNode = mve.getParentNode();
        return box;
    },

    gnrwdg_setCurrentPath:function(nodePath) {
        this.sourceNode.setRelativeData('.currentEditedPath',nodePath);
        this.mveNode.gnrwdg.setSource(nodePath+'?#node');
    }
});

dojo.declare("gnr.widgets.SearchBox", gnr.widgets.gnrwdg, {
    contentKwargs: function(sourceNode, attributes) {
        //var topic = attributes.nodeId+'_keyUp';
        attributes.onKeyUp = function(e) {
            var sourceNode = e.target.sourceNode;
            genro.dom.setClass(sourceNode.getParentNode(),'activeSearch',!isNullOrBlank(e.target.value));
            sourceNode.setRelativeData('.currentValue', e.target.value);
        };
        return attributes;
    },
    defaultDatapath:function(attributes) {
        return '.searchbox';
    },
    createContent:function(sourceNode, kw) {
        var searchOn = objectPop(kw, 'searchOn') || true;
        var searchDtypes;
        if (searchOn[0] == '*') {
            searchDtypes = searchOn.slice(1);
            searchOn = true;
        }
        var nodeId = objectPop(kw, 'nodeId');
        var menubag;
        var databag = new gnr.GnrBag();
        var defaultLabel = objectPop(kw, 'searchLabel') || 'Search';
        databag.setItem('menu_dtypes', searchDtypes);
        databag.setItem('caption', defaultLabel);
        databag.setItem('searchDelay',1000);
        this._prepareSearchBoxMenu(searchOn, databag);
        databag.setItem('value', '');
        sourceNode.setRelativeData(null, databag);
        var searchbox = sourceNode._('form',{autocomplete:'false',action:'javascript:void(0);'})._('table', {nodeId:nodeId})._('tbody')._('tr');
        var delay = objectPop(kw, 'delay') || objectPop(search_kw, 'delay') || 100;
        var search_kw = objectPop(kw,'search_kw') || {};
        sourceNode._('dataController', {'script':'genro.publish(searchBoxId+"_changedValue",currentValue,field,this.evaluateOnNode(search_kw));',
            'searchBoxId':nodeId,currentValue:'^.currentValue',field:'=.field',
            _userChanges:true,_delay:delay,search_kw:search_kw});
        var searchlbl = searchbox._('td');
        searchlbl._('div', {'innerHTML':'^.caption',_class:'buttonIcon searchboxLabel'});
        searchlbl._('menu', {'modifiers':'*',_class:'smallmenu',storepath:'.menubag',
            selected_col:'.field',selected_caption:'.caption',action:'SET .value = null;SET .currentValue = null;'});
        
        searchbox._('td')._('div',{_class:'searchInputBox',connect_onclick:function(e){
            if(e.target.tagName.toLowerCase()!='input'){
                var that = this;
                var finalize = function(){
                    that.setRelativeData('.value',null);
                    that.setRelativeData('.currentValue',null);
                    genro.dom.removeClass(that,'activeSearch');
                };
                genro.publish(nodeId+"_stopSearch",{inputSourceNode:this,finalize:finalize});
               
            }
        }})._('input', {'value':'^.value',connect_onkeyup:kw.onKeyUp,
                         parentForm:false,width:objectPop(kw,'width') || '6em',
                         tabindex:"-1",connect_focus:function(){this.domNode.select()}});
        sourceNode.registerSubscription(nodeId + '_updmenu', this, function(searchOn) {
            menubag = this._prepareSearchBoxMenu(searchOn, sourceNode.getRelativeData());
        });
        return searchbox;
    },
    _prepareSearchBoxMenu: function(searchOn, databag) {
        var menubag = new gnr.GnrBag();
        var i = 0;
        if (searchOn === true) {
            databag.setItem('menu_auto', menubag);
        }
        else {
            dojo.forEach(searchOn.split(','), function(col) {
                col = dojo.trim(col);
                var caption = col;
                if (col.indexOf(':') >= 0) {
                    col = col.split(':');
                    caption = col[0];
                    col = col[1];
                }
                col = col.replace(/[.@]/g, '_');
                menubag.setItem('r_' + i, null, {col:col,caption:caption,child:''});
                i++;
            });
        }
        databag.setItem('field', menubag.getItem('#0?col'));
        var defaultLabel = menubag.getItem('#0?caption');
        if (defaultLabel) {
            databag.setItem('caption', defaultLabel);
        }
        databag.setItem('menubag', menubag);
        //databag.setItem('value', '');
        //databag.setItem('currentValue',null);
    }

});

dojo.declare("gnr.widgets.PaletteGroup", gnr.widgets.gnrwdg, {
    createContent:function(sourceNode, kw) {
        var groupCode = objectPop(kw, 'groupCode');
        var palette_kwargs = objectExtract(kw, 'title,dockTo,top,left,right,bottom,height,width,maxable,resizable');
        palette_kwargs.dockButton = objectPop(kw,'dockButton') || objectExtract(kw,'dockButton_*');
        palette_kwargs['nodeId'] = palette_kwargs['nodeId'] || groupCode + '_floating';
        palette_kwargs['overflow'] = 'hidden'
        palette_kwargs.selfsubscribe_showing = function() {
            genro.publish('palette_' + this.getRelativeData('gnr.palettes._groups.pagename.' + groupCode) + '_showing'); //gnr.palettes?gruppopiero=palettemario
        };
        palette_kwargs['title'] = palette_kwargs['title'] || 'Palette ' + groupCode;
        var floating = sourceNode._('palette', palette_kwargs);
        var tab_kwargs = objectUpdate(kw, {selectedPage:'^gnr.palettes._groups.pagename.' + groupCode,groupCode:groupCode,_class:'smallTabs',margin:'2px'});
        var tc = floating._('tabContainer', tab_kwargs);
        return tc;
    }
});

dojo.declare("gnr.widgets.DownloadButton", gnr.widgets.gnrwdg, {
    createContent:function(sourceNode,kw){
        kw._rpcpars = objectUpdate({},objectExtract(kw,'rpc_*'));
        kw.action = "var pars = this.evaluateOnNode(_rpcpars); var method = objectPop(pars,'method'); genro.rpcDownload(method,pars)";
        var wdg = objectPop(kw,'wdg') || 'Button';
        return sourceNode._(wdg,kw);
    }

});

dojo.declare("gnr.widgets.DocumentFrame", gnr.widgets.gnrwdg, {
    createContent:function(sourceNode,kw){
        var framekw = objectExtract(kw,'frame_*');
        var barkw = objectExtract(kw,'pdf,print,download,title')
        var resource = objectPop(kw,'resource');
        var rpcCall = objectPop(kw,'rpcCall');
        var _delay = objectPop(kw,'_delay');
        var emptyMessage = objectPop(kw,'emptyMessage','Missing');

        var _if = objectPop(kw,'_if');
        var _reloader = objectPop(kw,'_reloader') || '^#WORKSPACE.reload_iframe';

        if(resource){
            resource = resource.split(':');
            kw['table'] = resource[0];
            kw['respath'] = resource[1];
            kw['pdf'] = kw.html?false:true;
            kw['record'] = kw.pkey;
            rpcCall = 'callTableScript';
        }

        framekw.frameCode = 'document_frame_#'
        framekw['_workspace'] = true;
        var frame = sourceNode._('framePane',framekw);
        var iframekw = {height:'100%',width:'100%',border:0,rpcCall:'callTableScript'};
        for (var k in kw){
            var val = kw[k];
            if(val && typeof(val)=='string'){
                val = val.replace('^','=');
            }
            iframekw['rpc_'+k] = val;
        }
        iframekw['_reloader'] = _reloader;
        iframekw['_if'] = '^#WORKSPACE.enabled';
        iframekw['rpcCall'] = rpcCall;
        iframekw['_delay'] = _delay;
        iframekw['documentClasses'] = true;
        objectUpdate(iframekw,objectExtract(kw,'iframe_*'));
        var iframe = frame._('ContentPane','center',{overflow:'hidden'})._('iframe',iframekw);
        var scriptkw = objectUpdate({'script':"SET #WORKSPACE.enabled = true; FIRE #WORKSPACE.reload_iframe;",'_delay':100,_if:_if,_else:'SET #WORKSPACE.enabled = false;'},kw);
        frame._('dataController',scriptkw);
        return frame;
    }
});

dojo.declare("gnr.widgets.IframeDiv", gnr.widgets.gnrwdg, {
    createContent:function(sourceNode, kw,children) {
        var value = objectPop(kw,'value');
        kw.border = kw.border || 0;
        sourceNode.attr.value = value;
        var iframe = sourceNode._('iframe',kw);
        var gnrwdg = sourceNode.gnrwdg;
        gnrwdg.zoom = objectPop(kw,'zoom');
        gnrwdg.iframeNode = iframe.getParentNode();
        return iframe;
    },

    gnrwdg_setValue:function(value,kw,trigger_reason){
        if(this.zoom){
            value = '<div style="zoom:'+this.zoom+'">'+value+'</div>';
        }
        this.iframeNode.domNode.contentWindow.document.body.innerHTML = value;
    }

});

dojo.declare("gnr.widgets.QuickEditor", gnr.widgets.gnrwdg, {
    createContent:function(sourceNode, kw,children) {
        kw['constrain_margin'] = '1px';
        kw['toolbar'] = kw['toolbar'] || false;
        var boxpars = objectExtract(kw,'height,width,z_index,position,top,left,right,bottom,_class');
        boxpars.height = boxpars.height;
        boxpars.position =  boxpars.position || 'relative'
        boxpars._class = (boxpars._class || '') +' quickEditorWrapper';
        var box = sourceNode._('div',boxpars);
        var editor = box._('div',{_class:'quickEditor'})._('div',{position:'absolute',top:'1px',bottom:'2px',left:'1px',right:'1px'})._('ckeditor',kw);
        box._('div',{_class:'quickEditorButton fakeButton'})._('div',{_class:'dijitArrowButtonInner',height:'17px',width:'18px',
                                                            cursor:'pointer',
                                                        connect_onclick:function(){
                                                            genro.dlg.dialogEditor(editor.getParentNode(),{});
                                                        }})
        return editor;
    },
    
    cell_onCreating:function(gridEditor,colname,colattr) {
        colattr['z_index']= 1;
        //colattr['position'] = 'fixed';
        colattr['constrain_overflow'] = 'hidden'
        colattr['height'] = colattr['height'] || '18px';
    }

});

dojo.declare("gnr.widgets.QuickTree", gnr.widgets.gnrwdg, {
    createContent:function(sourceNode, kw,children) {
        var value = objectPop(kw,'value');
        kw.storepath = sourceNode.absDatapath(value);
        return sourceNode._('tree',kw);
    }
});

dojo.declare("gnr.widgets.CodeEditor", gnr.widgets.gnrwdg, {
    createContent:function(sourceNode, kw) {
        var value = objectPop(kw,'value');
        var readOnly = objectPop(kw,'readOnly');
        if(readOnly==undefined){
            readOnly = true;
        }
        var editor_kwargs = objectExtract(kw,'editor_*');
        var tree_kwargs = objectExtract(kw,'tree_*');
        sourceNode.attr.value = value;
        var gnrwdg = sourceNode.gnrwdg;
        gnrwdg.rpcSourceBrowserGetter = objectPop(kw,'rpcSourceBrowser') || 'dev.rpcSourceBrowserGetter';
        gnrwdg.rpcSourceCodeGetter = objectPop(kw,'rpcSourceCodeGetter') || 'dev.loadModuleElement';
        gnrwdg.rpcSourceCodeSaver = objectPop(kw,'rpcSourceCodeSaver') || 'dev.saveModuleElement';

        sourceNode.attr._workspace = true;
        kw.frameCode = kw.frameCode ||  'CodeEditor_'+genro.getCounter();
        var frame = sourceNode._('FramePane','rootNode',kw);
        var bc = frame._('BorderContainer',{side:'center'});
        var pref = kw.frameCode?kw.frameCode+'_' : '';
       //var left = bc._('ContentPane','sourceBrowser',{region:'left',width:objectPop(tree_kwargs,'width','200px'),_class:'ce_sourceBrowserFrame'});
       //left._('tree','tree',{storepath:'#WORKSPACE.sourceBrowser',
       //        selfsubscribe_onSelected:function(kw){
       //            gnrwdg.onSelectedBrowserNode(kw);
       //        }});
        var center = bc._('ContentPane','sourceViewer',{region:'center',overflow:'hidden'});
       //var bar = frame._('slotBar',{slots:'2,browserOpener,2,selectedElement,*,savebtn,revertbtn,5',side:'top',_class:'ce_sourceViewerBar',height:'18px',background:'#efefef',toolbar:true});
       //bar._('SlotButton','browserOpener',{iconClass:'iconbox sitemap',action:function(){
       //    bc.getParentNode().widget.setRegionVisible('left','toggle');
       //}})
       //bar._('div','selectedElement',{innerHTML:'^#WORKSPACE.currentSelectedElement'})

       //bar._('SlotButton','savebtn',{iconClass:'iconbox save',label:'Save',action:function(){
       //    gnrwdg.saveChanges();
       //}});
       //bar._('SlotButton','revertbtn',{iconClass:'iconbox revert',label:'Revert'});
        var editor = center._('codemirror','sourceEditor',objectUpdate({value:'^#WORKSPACE.currentSourceElement',readOnly:readOnly,
                                                          config_mode:'python',config_lineNumbers:true,
                                                         config_indentUnit:4,config_keyMap:'softTab',
                                                            height:'100%'},editor_kwargs));
        gnrwdg.editorNode = editor.getParentNode();
        return bc;
    },

    gnrwdg_setValue:function(value){
        var module = this.sourceNode.getAttributeFromDatasource('value');
        var sourceNode = this.sourceNode;
        if(!module){
            sourceNode.setRelativeData('#WORKSPACE.currentSourceElement_loadedValue','');
            sourceNode.setRelativeData('#WORKSPACE.currentSourceElement','');
            return
        }
        genro.serverCall('dev.loadModuleSource',{module:module},function(result){
           //sourceNode.setRelativeData('#WORKSPACE.sourceBrowser',result.popNode('browser'));
           //var content = result.popNode('content');
           //sourceNode.setRelativeData('#WORKSPACE.currentSelectedElement',null);
            sourceNode.setRelativeData('#WORKSPACE.currentSourceElement_loadedValue',result);
            sourceNode.setRelativeData('#WORKSPACE.currentSourceElement',result);
        });
    },

    gnrwdg_onSelectedBrowserNode:function(kw){
        sourceNode.setRelativeData('#WORKSPACE.currentSelectedElement',kw.path);
        this.loadModuleElement();

    },
    gnrwdg_loadModuleElement:function(){
        var module = this.sourceNode.getAttributeFromDatasource('value');
        var currentSelectedElement = this.sourceNode.getRelativeData('#WORKSPACE.currentSelectedElement');
        var sourceNode = this.sourceNode;
        genro.serverCall(this.rpcSourceCodeGetter,{module:module,element:currentSelectedElement},function(result){
            sourceNode.setRelativeData('#WORKSPACE.currentSourceElement_loadedValue',result);
            sourceNode.setRelativeData('#WORKSPACE.currentSourceElement',result);
        });
    },
    gnrwdg_saveChanges:function(){
        var module = this.sourceNode.getAttributeFromDatasource('value');
        var currentSelectedElement = this.sourceNode.getRelativeData('#WORKSPACE.currentSelectedElement');
        var sourceNode = this.sourceNode;
        //it will save
    },
});

dojo.declare("gnr.widgets.TreeGrid", gnr.widgets.gnrwdg, {
    subtags : {column:true},

    createContent:function(sourceNode, kw,children,subTagItems) {
        sourceNode.attr._workspace = true;
        var gnrwdg = sourceNode.gnrwdg;
        var that = this;
        var columns = objectPop(kw,'columns');
        var boxpars = objectExtract(kw,'box_*');
        gnrwdg.width = 0;
        gnrwdg.labelAttribute = objectPop(kw,'labelAttribute');
        gnrwdg.headers=objectPop(kw,'headers');
        gnrwdg.footers=objectPop(kw,'footers');
        gnrwdg.headers_footers_kw = objectExtract(kw,'headers_*',false,true);
        objectUpdate(gnrwdg.headers_footers_kw,objectExtract(kw,'footers_*',false,true));

        if(!columns){ 
            columns = '^#WORKSPACE.columns';
            sourceNode.registerDynAttr('columns');
        }
        gnrwdg.columns_bag = this._getColumnsBag(sourceNode,columns,subTagItems['column']);
        var searchColumn = gnrwdg.columns_bag.getNode('#0').attr.field;
        var checked_attr = objectExtract(kw,'checked_*',true);
        var hasCheckbox = objectNotEmpty(checked_attr) || kw.onChecked;
        var defaultKw = {
            autoCollapse:true,
            hideValues:true,
            background:'white',
            searchColumn:searchColumn,
            _class:hasCheckbox?'treegrid branchtree' :'treegrid branchtree noIcon',
            connect__expandNode:function(){
                gnrwdg.updateScroll();
            },
            labelCb:function(store){return gnrwdg.labelCb(this,store)}
        };
        var boxclass = hasCheckbox?'treegridcheckbox treeGridLayout ':'treeGridLayout ';
        var box = sourceNode._('div',objectUpdate({_class:boxclass+(objectPop(kw,'_class') || ''),
            onCreated:function(){
            var that = this;
            this.watch('setWidth',function(){
                var currentWidth = that.domNode.clientWidth;
                if(!that._isBuilding && currentWidth!=gnrwdg.width){
                    gnrwdg.width = currentWidth;
                    gnrwdg.refresh();
                }
            },function(){});
        }},boxpars));
        gnrwdg.layoutNode = box.getParentNode();
        if (gnrwdg.headers){
            gnrwdg.headerNode = box._('div',{_class:'treeGridHeader'}).getParentNode();
        }
        if(gnrwdg.footers){
            gnrwdg.footerNode = box._('div',{_class:'treeGridFooter'}).getParentNode();
        }
        var center = box._('div',{_class:'treeGridCenter'});
        gnrwdg.scrollerNode = box._('div',{_class:'treeGridScroller'}).getParentNode();
        var tree = center._('tree',objectUpdate(defaultKw,kw));
        gnrwdg.centerNode = center.getParentNode();
        gnrwdg.treeNode = tree.getParentNode();
        gnrwdg.absStorepath = gnrwdg.treeNode.absDatapath(kw.storepath);
        gnrwdg.treeNode.componentHandler = gnrwdg;
        return tree
    },

    gnrwdg_footersHeadersHandler:function(w){
        var ws = w+'s';
        if(this[ws]){
            this[w+'Node'].domNode.innerHTML = null;
            var hf = this[ws]==true? ['']:this[ws].split(',');
            var that = this;
            hf.forEach(function(h){
                var pars = objectExtract(that.headers_footers_kw,h?ws+'_'+h+'_*':ws+'_*',true);
                that.setHeaderFooter(h?w+'_'+h:w,pars,w);
            });
        }
    },

    gnrwdg_refresh:function(){
        var that = this;
        this.mainCellSize = parseInt(this.columns_bag.getAttr('#0').size);
        if(!this.mainCellSize){
            var otherSize = 0;
            this.columns_bag.getNodes().slice(1).forEach(n=>otherSize+=parseInt(n.attr.size));
            this.mainCellSize = Math.max((this.centerNode.domNode.clientWidth-70-otherSize),200);
        }
        this.treeNode.widget.updateLabels();
        this.footersHeadersHandler('header');
        this.footersHeadersHandler('footer');
        this.centerNode.domNode.style.top = this.headerNode? this.headerNode.domNode.clientHeight+1+'px':'0px';
        this.centerNode.domNode.style.bottom = this.footerNode?this.footerNode.domNode.clientHeight+1+'px':'0px';
        this.currentScroll = 0;
        this.setScroller();
        setTimeout(function(){
            that.updateScroll();
        },1);
    },

    gnrwdg_setScroller:function(){
        this.scrollerNode._value.popNode('viewport');
        var layoutDomNode = this.layoutNode.domNode;
        var gnrwdg = this;
        var viewport = this.scrollerNode._('div','viewport',{position:'absolute',right:0,bottom:0,top:0,width:this.viewPortWidth+'px',overflow:'auto',
                        connect_onscroll:function(evt){
                            gnrwdg.currentScroll = evt.target.scrollLeft;
                            gnrwdg.updateScroll();
                        }});
        viewport._('div',{height:'2px',width:this.cellsWidth+'px'})
    },

    gnrwdg_updateScroll:function(){
        var that = this;
        dojo.query('.treeerow_viewport',this.layoutNode.domNode).forEach(function(n){
                            n.style.overflow = 'scroll'
                            n.scrollLeft = that.currentScroll;
                            n.style.overflow = 'hidden'
                        });
    },

    htmlCellContent:function(content,cell){
        if(content && content.attr){
            content = cell.contentCb? funcApply(cell.contentCb,{field:cell['field']},content):content.attr[cell['field']];
        }
        content = content || cell.emptyValue;
        var format = cell['format'];
        var dtype = cell['dtype'] || 'T';
        content = _F(content,format,dtype) || '&nbsp;';
        return '<div class="treeCellContent">'+content+'</div>'
    },

    gnrwdg_setHeaderFooter:function(contentKey,pars,mode){
        if(!this.width){
            return;
        }
        if(pars.hidden){
            return
        }
        var columns_bag = this.columns_bag;
        var mainCell = columns_bag.getAttr('#0');
        mainCell = this.sourceNode.evaluateOnNode(mainCell);
        var maxwidth = this.width;        
        var currx = 0;
        var cell;
        var l = [];
        var htmlCellContent = this.gnr.htmlCellContent;
        var n;
        var sn = this.sourceNode;
        var colkeys = this.columns_bag.keys().slice(1);
        var tplpars = {};
        var mainCellSize = this.mainCellSize+21;//tree margin
        var colswidth = maxwidth-this.mainCellSize-35;//border
        var customKw,cellstyle,objStyle,conten,sizet;
        colkeys.forEach(function(key){
            n = columns_bag.getNode(key);
            cell = sn.evaluateOnNode(n.attr);
            objectUpdate(cell,pars);
            customKw = objectExtract(cell,contentKey+'_*');

            objectExtract(cell,'dtype,format,style,cellClass');
            objectUpdate(cell,customKw);
            if(!cell.hidden){
                size=parseInt(cell.size);
                if ( stringEndsWith((size+''),'%') ){
                    size=Math.round(maxwidth*parseInt(size)/100)
                }
                objStyle=objectUpdate(objectFromStyle(cell._style),
                                         sn.evaluateOnNode(genro.dom.getStyleDict(objectUpdate({},cell), [ 'width'])))
                objStyle['width']=size+'px'
                cellstyle=objectAsStyle(objStyle)
                content = cell[contentKey];
                cell.dtype = cell.dtype || guessDtype(content);
                l.push('<div class="treecell cell_'+(cell.dtype || 'T') +' '+(cell.cellClass || '')+' " style="'+cellstyle+'">'+htmlCellContent(content,cell)+'</div>');
                currx += size+1 || 0;
            }
        })
        var storeNode = genro.getDataNode(this.absStorepath);
        var rowwidth = maxwidth;
        objectExtract(mainCell,'dtype,format,style,cellClass');
        objectUpdate(mainCell,pars);
        customKw = objectExtract(mainCell,contentKey+'_*');
        objectUpdate(mainCell,customKw);
        objStyle=objectUpdate(objectFromStyle(mainCell._style),
        sn.evaluateOnNode(genro.dom.getStyleDict(objectUpdate({},mainCell), [ 'width'])))
        objStyle['width']=mainCellSize+'px';
        objStyle['overflow'] = 'hidden';
        cellstyle=objectAsStyle(objStyle)
        this.cellsWidth = currx;
        this.viewPortWidth = colswidth;
        tplpars['maincell'] = '<div class="treecell maincell'+(mainCell.cellClass || '')+' " style="'+cellstyle+'"><div class="treeCellContent">'+(mainCell[contentKey] || '&nbsp;')+'</div></div>';
        tplpars['columns'] = '<div class="treeerow_viewport" style="width:'+colswidth+'px;"><div class="treerow_columns" style="width:'+(currx+1)+'px;">'+l.join('')+'</div></div>'
        
        var elem = document.createElement('div');
        elem.innerHTML = dataTemplate('<div class="treerow treerow_'+mode+'" style="width:'+rowwidth+'px;">$maincell $columns</div>',tplpars);
        this[mode+'Node'].domNode.appendChild(elem.removeChild(elem.firstChild)); 
        
        //return "innerHTML:<div class='treerow treerow_level_"+level+"' style='width:"+rowwidth+"px;'>"+l.join('')+"</div>";
    },



    gnrwdg_labelCb:function(item,store){
        if(!this.width){
            return;
        }
        
        var k = 10;
        var mainLabel = item.label;
        var columns_bag = this.columns_bag;
        var mainCell = columns_bag.getAttr('#0');
        var maxwidth = this.width-35;
        var colswidth = maxwidth-this.mainCellSize ;
        var currx = 0;
        var cell;
        var l = [];
        var htmlCellContent = this.gnr.htmlCellContent;
        var n;
        var sn = this.sourceNode;
        var colkeys = this.columns_bag.keys().slice(1);
        var tplpars = {};

        colkeys.forEach(function(key){
            n = columns_bag.getNode(key);
            cell = sn.evaluateOnNode(n.attr);
            if(!cell.hidden){
                var size=parseInt(cell.size);
                if ( stringEndsWith((size+''),'%') ){
                    size=Math.round(maxwidth*parseInt(size)/100)
                }
                var objStyle=objectUpdate(objectFromStyle(cell._style),
                                         sn.evaluateOnNode(genro.dom.getStyleDict(objectUpdate({},cell), [ 'width'])))
                objStyle['width']=size+'px'
                var cellstyle=objectAsStyle(objStyle)       
                l.push('<div class="treecell cell_'+(cell.dtype || 'T') +' '+(cell.cellClass || '')+' " style="'+cellstyle+'">'+htmlCellContent(item,cell)+'</div>');
                currx += size+1 || 0;
            }
        })
        var storeNode = genro.getDataNode(this.absStorepath);
        var level = (item.parentshipLevel(storeNode)-1);
        var folder = store.hasAttribute(item,'#v')?' treerow_folder ':'';
        var rowwidth = maxwidth-level*k;
        var objStyle=objectUpdate(objectFromStyle(mainCell._style),
        sn.evaluateOnNode(genro.dom.getStyleDict(objectUpdate({},mainCell), [ 'width'])))
        objStyle['width']=(this.mainCellSize-level*k)+'px';
        objStyle['overflow'] = 'hidden';
        var cellstyle=objectAsStyle(objStyle)
        this.cellsWidth = currx;
        this.viewPortWidth = colswidth;
        tplpars['maincell'] = '<div class="treecell maincell cell_'+(mainCell.dtype || 'T')+' '+(mainCell.cellClass || '')+' " style="'+cellstyle+'">'+htmlCellContent(item,mainCell)+'</div>';
        tplpars['columns'] = '<div class="treeerow_viewport" style="width:'+colswidth+'px;"><div class="treerow_columns" style="width:'+currx+'px;">'+l.join('')+'</div></div>'
        return dataTemplate('innerHTML:<div class="treerow treerow_level_'+level+ folder+'">$maincell $columns</div>',tplpars)
        
        //return "innerHTML:<div class='treerow treerow_level_"+level+"' style='width:"+rowwidth+"px;'>"+l.join('')+"</div>";
    },

    _getColumnsBag:function(sourceNode,columns,childrenColumns){
        var columns_bag = sourceNode.getRelativeData(columns) || new gnr.GnrBag();;
        childrenColumns.forEach(function(n){
            var attr = n.attr;
            attr.field = attr.field || n.label;
            columns_bag.setItem(attr.field,null,attr);
        })
        return columns_bag;
    }

});

dojo.declare("gnr.widgets.VideoPlayer", gnr.widgets.gnrwdg, {
    createContent:function(sourceNode, kw,children) {
        var frameKw = objectExtract(kw,'height,width,region,title,border,splitter,_class,style,frameCode,datapath,rounded');
        var subtitlePane = objectPop(kw,'subtitlePane');
        frameKw.frameCode = frameKw.frameCode || 'videoplayer_'+genro.getCounter();
        var frame = sourceNode._('FramePane',frameKw);
        var slots = objectPop(kw,'slots');
        var manageCue = objectPop(kw,'manageCue');
        var controllerSide = objectPop(kw,'controllerSide') || 'top';
        var center = frame._('BorderContainer',{side:'center',
                            connect_resize:function(){
                                var minH = 30;
                                var maxH = 100;
                                var bcdn = this.widget.domNode;
                                var top = this.widget._top;
                                var centerDN = this.widget._center;
                                var video = top.children[0];
                                var subH = bcdn.clientHeight - top.clientHeight;
                                if(subH<(minH-3)){
                                    var topH = (bcdn.clientHeight-minH);
                                    video.style.height = topH+'px';
                                    video.style.width = null;
                                }else if(top.clientWidth<video.clientWidth){
                                    video.style.height = null;
                                    video.style.width = '100%';
                                }else if(subH>maxH){
                                    video.style.height = null;
                                    video.style.width = '100%';
                                }
                                /*else{
                                    video.style.height = null;
                                    video.style.width = '100%';
                                }*/

                                //console.log('resizing top  ',top.clientHeight,top.clientWidth,
                                //            '\nresizing video',video.clientHeight,video.clientWidth,
                                //            '\nresizing bc   ',bcdn.clientHeight,bcdn.clientWidth);
                            }
                            });
        var gnrwdg = sourceNode.gnrwdg;
        kw.src = '^.videoSrc';
        kw.currentTime = '^.currentTime';
        kw.playing = '.playing';
        kw.width = kw.video_width || '100%';
        //kw.height = kw.video_height || '100%';
        kw.border = kw.video_border || 0;
        var urlPars = objectExtract(kw,'url,timerange');
        gnrwdg.urlPars = urlPars;
        kw.connect_loadedmetadata = function(){
            gnrwdg.onLoadedVideo(this);
            this.getParentNode().getParentNode().widget.layout()
        }
        sourceNode.attr.videoCurrentTime = kw.currentTime
        if(frameKw.frameCode && !kw.nodeId){
            kw.nodeId = frameKw.frameCode +'_video';
        }
        gnrwdg.videoNodeId =kw.nodeId;
        center._('dataFormula',{path:'.videoSrc',formula:"url?genro.addParamsToUrl(url,{'#t':timerange}):null;",
                                url:urlPars.url,timerange:urlPars.timerange,_onBuilt:true,_delay:1});
        center._('dataFormula',{path:'.playerTime',
                                formula:"currentTime-(range_start||0)",
                                currentTime:'^.currentTime',
                                range_start:'=.range_start',
                                _if:'_triggerpars.kw.reason=="player" && !editingPlayerSearch',
                                editingPlayerSearch:'=.editingPlayerSearch'});
        center._('dataController',{script:"var currentTime = playerTime+range_start; if(currentTime>=range_end){ FIRE .resetPlayer;}else{ SET .currentTime=currentTime;}",playerTime:'^.playerTime',
                                range_start:'=.range_start',range_end:'=.range_end'});
        center._('dataController',{script:'genro.domById(videoNodeId).pause(); SET .playerTime = 0;',_fired:'^.resetPlayer',videoNodeId:gnrwdg.videoNodeId})
        
        var video = center._('ContentPane',{region:'top',overflow:'hidden'})._('video','video',kw);
        if(subtitlePane){
            var subpane = center._('ContentPane',{region:'center',min_height:'100px'})._('div',{innerHTML:'^.mainsub.text'});
            gnrwdg.subtitleNode = subpane.getParentNode();
        }
        gnrwdg.preparePlayerBar(frame,slots,manageCue,controllerSide);
        return video;
    },

    gnrwdg_onLoadedVideo:function(videoSourceNode){
        var videoDomNode = videoSourceNode.domNode;
        var videoDuration = Math.round(videoDomNode.duration*10)/10;
        var playerDuration = videoDuration;
        var sn = this.sourceNode;
        sn.setRelativeData('.duration', videoDuration);
        var urlPars = sn.evaluateOnNode(this.urlPars);
        var timerange = urlPars.timerange;
        if(timerange){
            var r = timerange.split(',').map(function(n){return parseInt(n)});
            sn.setRelativeData('.range_start',r[0]);
            sn.setRelativeData('.range_end',r[1]);
            playerDuration = Math.round((r[1]-r[0])*10)/10;
        }else{
            sn.setRelativeData('.range_start',0);
            sn.setRelativeData('.range_end',playerDuration);
        }
        sn.setRelativeData('.playerTime',0);
        sn.setRelativeData('.playerDuration',playerDuration);
    },

    gnrwdg_preparePlayerBar:function(frame,slots,manageCue,controllerSide){
        slots = slots || '10,playbutton,playerslider,searchBox,*'
        if(manageCue){
            slots = slots+',cuebutton,10';
        }        
        var bar = frame._('SlotBar','bar',{slots:slots,side:controllerSide,height:'21px',toolbar:true,playerslider_width:'100%'});
        var slotsKw = {};
        var videoNodeId = this.videoNodeId;
        slotsKw.playbutton = {tag:'slotButton',
            label:'==_playing?"Pause":"Play"',
             action:function(){
                var kw = arguments[arguments.length-1]
                var _video = genro.domById(kw._videoNodeId); 
                if(kw._playing){
                    _video.pause()
                }else{
                    _video.play()
                };
             },
             //'var _video = genro.domById(_videoNodeId); if(_playing){_video.pause()}else{_video.play()};',
            _playing:'^.playing',
            iconClass:'==_playing?"player_pause":"player_play"',
            _videoNodeId:this.videoNodeId
        };
        slotsKw.playerslider = {tag:'horizontalSlider',
            value:'^.playerTime',
            minimum:0, 
            maximum:'^.playerDuration', 
            intermediateChanges:false,
            width:'100%',parentForm:false
        };
        slotsKw.searchBox = 'videoSearchBox';
        slotsKw.cuebutton = {
            tag:'slotButton',
            label:"==_start_time?'Make cue':'Start cue';",
            _start_time:'^.start_time',
            iconClass:'==_start_time? "iconbox comment_check":"iconbox comment_plus"',
            action:function(){
                var start_time = this.getRelativeData('.start_time');
                var currentTime = this.getRelativeData('.currentTime');

                var video = genro.domById(videoNodeId);
                if(start_time){
                    video.pause();
                    this.setRelativeData('.start_time',null);
                    video.sourceNode.publish('addCue',{start_time:start_time,end_time:currentTime});
                }else{
                    if(!this.getRelativeData('.playing')){
                        video.play();
                    }
                    this.setRelativeData('.start_time',currentTime);
                }
            }
        };
        var that = this;
        slots.split(',').forEach(function(s){
            if(s in slotsKw){
                var handler = slotsKw[s];
                if(typeof(handler)=='string'){
                    that[handler](bar,s);
                }else{
                    var skw = objectUpdate({},handler);
                    var tag = objectPop(skw,'tag');
                    bar._(tag,s,skw);
                }
            }
        });
    },
    gnrwdg_videoSearchBox:function(bar,slotName){
        var sb = bar._('div',slotName)
        var fb = genro.dev.formbuilder(sb,1,{border_spacing:'1px',font_size:'.9em'});
        var videoNodeId = this.videoNodeId;
        var that = this;

        fb.addField('callbackSelect',{value:'^.playerTime',width:'6em',
                                      lbl_text_align:'right',
                                      lbl:_T('Search'),
                                      lbl_color:'#444',
                                      rounded:6,
                                      parentForm:false,
                                      validate_onAccept:function(){
                                        this.widget.focusNode.blur();
                                      },
                                      auxColumns:'start,end',
                                      _class:'numberTextBox',
                                      connect_onFocus:function(){
                                           this.setRelativeData('.editingPlayerSearch',true);
                                      },
                                      connect__onBlur:function(){
                                           this.setRelativeData('.editingPlayerSearch',false);
                                      },

                                      callback:function(kw){
                                            var _id = kw._id;
                                            var _querystring = kw._querystring;
                                            var videoDomNode = genro.domById(videoNodeId);
                                            var sn = videoDomNode.sourceNode;
                                            var currentTextTrack = sn.getAttributeFromDatasource('searchTrack') || 0;
                                            var cues = videoDomNode.textTracks[currentTextTrack].cues;
                                            var range_start = sn.getRelativeData('.range_start');
                                            var range_end = sn.getRelativeData('.range_end');
                                            var data = [];
                                            if(_querystring){
                                                _querystring = _querystring.slice(0,-1).toLowerCase();
                                                if(parseFloat(_querystring)>=0){
                                                    _id = parseFloat(_querystring);
                                                    _querystring = null;
                                                }
                                            }
                                            if(_querystring){
                                                dojo.forEach(cues,function(c){
                                                    if(c.startTime<range_start || c.startTime>range_end){
                                                        return;
                                                    }
                                                    var start_offset = r[0] || 0;
                                                    var startTime = c.startTime -start_offset;
                                                    var endTime = c.endTime - start_offset;
                                                    if(c.text.indexOf(_querystring)>=0){
                                                        data.push({txt:c.text,_pkey:startTime,start:startTime,end:endTime,
                                                                  caption:_F(startTime,'###.00')})
                                                    }
                                                })
                                            }else if(_id){
                                                data = [{_pkey:_id,caption:_F(_id,'###.00'),start:_id,endTime:_id,txt:_F(_id,'###.00')}];
                                            }
                                            return {data:data,headers:'txt:Text,start:Start,end:End'}
                                      }
                                    });

    }

});
dojo.declare("gnr.widgets.GridGallery", gnr.widgets.gnrwdg, {
    createContent:function(sourceNode, kw) {
        var grid_pars = objectExtract(kw,'items,columns');
        grid_pars.selfDragRows = genro.isDeveloper;
        objectUpdate(grid_pars,objectExtract(kw,'grid_*'));
        var onContentSaved = objectPop(kw,'onSaved');
        var items = objectPop(grid_pars,'items');
        var docpars = objectExtract(kw,'di_*');
        var navigation = objectPop(kw,'navigation');
        var sharedObjectId = objectPop(kw,'sharedObjectId');
        
        if(!items && objectNotEmpty(docpars)){
            items = '^gnr.language?=#v?"_doc.content.'+docpars.store+'.'+docpars.key+'.'+docpars.contentpath+'."+#v:"emptypath"';
        }
        if(onContentSaved){
            onContentSaved = funcCreate(onContentSaved);
        }else{
            onContentSaved = function(){
                sourceNode.publish('onContentSaved');
            }
        }
        var viewer_pars = objectExtract(kw,'viewer_*');
        var itemspath = sourceNode.absDatapath(items);
        var grid_region = grid_pars.region || 'left';
        var gnrwdg = sourceNode.gnrwdg;

        kw.selfsubscribe_toggle_grid = function(){
            this.widget.setRegionVisible(grid_region,'toggle');
        }
        kw.selfsubscribe_next = function(){
            var next_idx = this.getRelativeData('#WORKSPACE.selectedIndex')+1;
            var tot = this.getRelativeData('#WORKSPACE.total_pages')-1;
            next_idx = (next_idx>=tot)?tot:next_idx;
            this.setRelativeData('#WORKSPACE.selectedIndex',next_idx);
        }
        kw.selfsubscribe_prev = function(){
            var prev_idx = this.getRelativeData('#WORKSPACE.selectedIndex')-1;
            this.setRelativeData('#WORKSPACE.selectedIndex',prev_idx>=0?prev_idx:0);
        }
        kw.selfsubscribe_zoom = function(){
            var s = gnrwdg.viewerBC.widget.setRegionVisible('top','toggle');
            var dn = gnrwdg.iframecontainerNode.domNode;
            genro.dom.setClass(gnrwdg.iframecontainerNode,'expanded_gallery_iframe',!s);
            if(s===false){
                gnrwdg.iframecontainerNode._zoomed = true;
                dojo.body().appendChild(dn);
            }else{
                gnrwdg.iframecontainerNode._zoomed = false;
                gnrwdg.centerframeNode.widget.domNode.appendChild(dn);
            }
        }
        var showcase = objectPop(kw,'showcase');
        if(sourceNode.isPointerPath(items)){
            grid_pars.dynamicStorepath = itemspath;
        }else{
            grid_pars.value = itemspath;
        }
        
        grid_pars.autoSelect = true;
        grid_pars['store_sortedBy'] = '_row_count';
        kw._workspace = true;
        kw.design = kw.design || 'sidebar';
        if(showcase){
            kw._class = (kw._class || '')+' showcase_' +(showcase==true?'light':showcase);
        }
        var bc = sourceNode._('BorderContainer',kw);
        var rootnode = bc.getParentNode();
        rootnode._('dataFormula',{path:'#WORKSPACE.total_pages',
                    formula:'typeof(v)=="string"?(this.getRelativeData(v)?this.getRelativeData(v).len():0):(v?v.len():0)',v:'^'+itemspath});
        if(showcase && sharedObjectId && genro.wsk.wsroot){
            sourceNode._('SharedObject',{shared_id:sharedObjectId,shared_path:'showcase_remote',expire:60});
            rootnode._('dataFormula',{path:'showcase_remote',
                                        script:"new gnr.GnrBag({slide_index:slide_index,minutes:minutes,comment:comment,total_pages:total_pages,zoomEnabled:zoomEnabled,current_time:current_time,started:started});",
                                        slide_index:'^#WORKSPACE.selectedIndex',
                                        minutes:'=#WORKSPACE.minutes',
                                        comment:'=#WORKSPACE.comment',
                                        total_pages:'=#WORKSPACE.total_pages',
                                        zoomEnabled:'=#WORKSPACE.iframe_src?=#v?true:false',
                                        current_time:'=showcase_remote.current_time',
                                        started:'=showcase_remote.started',
                                        _delay:1});
            rootnode._('dataController',{script:"this.getParentNode().publish(command);",command:'^showcase_remote.command',_userChanges:true});
        }

        if(showcase){
            bar = bc._('ContentPane',{region:'bottom',_class:'showcase_bar'})._('slotBar',{slots:'5,toggle,15,prev,5,next,*,slide_cnt,2',side:'bottom'});
            bar._('lightbutton','toggle',{tip:_T('!!Toggle'),action:function(){
                rootnode.publish('toggle_grid');
            },_class:'showcase_button showcase_toggle'});
            bar._('lightbutton','prev',{tip:_T('!!Prev'),action:function(){
                rootnode.publish('prev');
            },_class:'showcase_button showcase_prev'});
            bar._('lightbutton','next',{tip:_T('!!Next'),action:function(){
                rootnode.publish('next');
            },_class:'showcase_button showcase_next'});
            bar._('div','slide_cnt',{template:"$_curr/$_tot ($_minutes)",_curr:"^#WORKSPACE.selectedIndex?=#v+1",
                                        _tot:'^#WORKSPACE.total_pages',_minutes:'^#WORKSPACE.minutes?=#v?#v:"..."',width:'6em',
                                        _class:'showcase_counter'});
            grid_pars.hidden = true;
        }
        var dpath = rootnode.absDatapath('#WORKSPACE.curr_datapath');
        var emptypath =  rootnode.absDatapath('#WORKSPACE.emptypath');
        sourceNode.setRelativeData(dpath,emptypath);
        
        grid_pars.connect_onSelected = function(rowIndex){
            if(rowIndex>=0 && this.widget.storebag().len()>0){
                this.setRelativeData(dpath,
                    this.widget.collectionStore().itemByIdx(rowIndex).getFullpath().slice(5));
                setTimeout(function(){
                    gnrwdg.viewerBC.widget.resize();
                },1)
            }
        }
        grid_pars.selected_minutes = rootnode.absDatapath('#WORKSPACE.minutes');
        grid_pars.selected_comment = rootnode.absDatapath('#WORKSPACE.comment');
        grid_pars.selected_iframe_src = rootnode.absDatapath('#WORKSPACE.iframe_src');

        grid_pars.selectedIndex = '^'+rootnode.absDatapath('#WORKSPACE.selectedIndex');
        grid_pars.selfsubscribe_addrow = function(addkw){
                                                var grid = this.widget;
                                                setTimeout(function(){
                                                    gnrwdg.addNewPage(grid,addkw);
                                                },500);
        }
        var gridpane_kw = objectExtract(grid_pars,'width,_class,drawer,hidden');
        gridpane_kw._class = showcase?'grid_gallery_grid_showcase': 'grid_gallery_grid noheader';
        objectUpdate(gridpane_kw,objectExtract(grid_pars,'drawer_*'));
        var gp = bc._('ContentPane','gridpane',objectUpdate({region:'left'},gridpane_kw))
        var g = gp._('quickGrid','grid',grid_pars);
        if(genro.isDeveloper){
            //g._('tools',{tools:'addrow,delrow',position:'BR'});
            g._('tools',{tools:'delrow,addrow',
                    custom_tools:{addrow:{content_class:'iconbox add_row',ask:{title:_T('New Page'),
                            fields:[{name:'label',lbl:'Label',validate_notnull:true},
                                    {name:'iframe_src',lbl:'Src'}]}
                                    }},position:'BR'});
            g._('column',{field:'_row_count',counter:true,hidden:!showcase,name:'N.',width:'3em'});
            g._('column',{field:'label',name:'Label',width:'100%',edit:true});
            if(showcase){
                g._('column',{field:'minutes',name:'Min',width:'4em',dtype:'L',edit:true});
            }
        }else{
            g._('column',{field:'_row_count',counter:true,hidden:true})
            g._('column',{field:'label',name:'Label',width:'100%'});
        }
        var content_kw = objectExtract(kw,'content_*');
        content_kw.innerHTML = '^.content';
        content_kw._class = 'doc_item selectable '+ (content_kw._class || '');
        content_kw.min_height = '30px';
        content_kw.stlyes = '^.';
        if(genro.isDeveloper){
            content_kw.connect_ondblclick = function(){
                    var that = this;
                    genro.dlg.prompt(_T('Edit'),{dlg_noModal:true,
                        widget:function(pane){
                            var tc = pane._('tabContainer',{height:'600px',width:'1000px',margin:'2px'});
                            tc._('ContentPane',{title:'Content',overflow:'hidden'})._('ckeditor',{value:'^.content'});
                            var pane = tc._('ContentPane',{title:'Metadata',overflow:'hidden'})
                            var fb = genro.dev.formbuilder(pane._('div',{margin:'10px'}),3,{border_spacing:'1px',width:'100%',margin_bottom:'12px'});
                            fb.addField('textbox',{value:'^.iframe_src',width:'25em',lbl_text_align:'right',
                                        lbl:_T('Example src'),lbl_color:'#444',parentForm:false,colspan:3});
                            fb.addField('numberTextBox',{value:'^.scale_min',width:'6em',lbl_text_align:'right',
                                        lbl:_T('Scale min'),lbl_color:'#444',parentForm:false});
                            fb.addField('numberTextBox',{value:'^.scale_max',width:'6em',lbl_text_align:'right',
                                        lbl:_T('Scale max'),lbl_color:'#444',parentForm:false});
                            fb.addField('numberTextBox',{value:'^.minutes',width:'6em',lbl_text_align:'right',
                                        lbl:_T('Minutes'),lbl_color:'#444',parentForm:false});
                            fb.addField('SimpleTextArea',{value:'^.comment',width:'40em',height:'450px',lbl_text_align:'right',
                                        lbl:_T('Comment'),lbl_color:'#444',parentForm:false,lbl_vertical_align:'top',colspan:3});
                            tc._('ContentPane',{title:'HTML Source',overflow:'hidden'})._('codemirror',{value:'^.content',config_mode:'htmlmixed',height:'100%',config_lineNumbers:true});
                            tc._('ContentPane',{title:'Content Styles',overflow:'hidden'})._('codemirror',{value:'^.content_styles',config_mode:'css',config_lineNumbers:true,height:'100%'});
                        },action:function(value){
                            that.setRelativeData('.content',value.getItem('content'));
                            that.setRelativeData('.comment',value.getItem('comment'));
                            that.setRelativeData('.minutes',value.getItem('minutes'));
                            that.setRelativeData('.scale_min',value.getItem('scale_min'));
                            that.setRelativeData('.scale_max',value.getItem('scale_max'));
                            that.setRelativeData('.content_styles',value.getItem('content_styles'));
                            that.setRelativeData('.iframe_src',value.getItem('iframe_src'));
                            onContentSaved();
                        },
                        dflt:this.getRelativeData().deepCopy()
                    });
            }
        }
        var viewer = bc._('BorderContainer',objectUpdate({region:'center',_class:'grid_gallery_box',datapath:'^'+dpath},viewer_pars))
        sourceNode.gnrwdg.viewerBC = viewer.getParentNode();
        content_kw.overflow = 'auto';
        content_kw.style = '^.content_styles';
        var vtop = viewer._('ContentPane',{region:'top'})
        vtop._('div',content_kw);
       //if(showcase){
       //    vtop._('div',{position:'absolute',top:'5px',right:'5px',_class:'iconbox comment',hidden:'^.comment?=!#v'})._('tooltipPane')._('div',{innerHTML:'^.comment',min_height:'150px',width:'200px'});
       //}
        centerframe = viewer._('ContentPane',{region:'center',overflow:'hidden'});
        var iframecontainer = centerframe._('div',{_class:'gallery_iframe_container',hidden:'^.iframe_src?=!#v'});
        var iframe = iframecontainer._('iframe',{src:'^.iframe_src',height:'100%',width:'100%',border:0,
                                                onLoad:function(){
                                                    var smax = gnrwdg.viewerBC.getRelativeData('.scale_max');
                                                    var smin = gnrwdg.viewerBC.getRelativeData('.scale_min');
                                                    this.contentDocument.body.style.zoom = this.parentNode.sourceNode._zoomed? (smax || null):(smin || null);
                                                }});
        gnrwdg.iframecontainerNode = iframecontainer.getParentNode();
        gnrwdg.iframeNode = iframe.getParentNode();
        gnrwdg.centerframeNode = centerframe.getParentNode();
        
        iframecontainer._('div',{position:'absolute',_class:'iconbox resize',position:'absolute',top:'2px',right:'2px',z_index:2,
                       connect_onclick:function(){
                            rootnode.publish('zoom');
                       },
                        hidden:'^.iframe_src?=!#v'})
        return bc;
    },

    gnrwdg_addNewPage:function(grid,kw){
        var label = kw.label;
        var iframe_src = kw.iframe_src;
        var dtype = kw.dtype;
        if(!label){
            genro.dlg.floatingMessage(this.containerNode,{messageType:'error',message:'Missing Label'})
            return;
        }
        grid.addRows([{'label':label,iframe_src:iframe_src}]);
    }
});

dojo.declare("gnr.widgets.QuickGrid", gnr.widgets.gnrwdg, {
    subtags : {column:true,
               selectionstore:true,
               tools:true},

    createContent:function(sourceNode, kw,children,subTagItems) {
        objectPop(kw,'_workspace')
        sourceNode.attr._workspace = kw.nodeId || true;
        var gnrwdg = sourceNode.gnrwdg;
        var value = objectPop(kw,'value');
        var dynamicStorepath = objectPop(kw,'dynamicStorepath');
        var columns = objectPop(kw,'columns');
        sourceNode.attr.fields = objectPop(kw,'fields');
        gnrwdg.guessColumns = sourceNode.attr.fields;
        gnrwdg.infoInCellAttributes = objectPop(kw,'infoInCellAttributes');
        if(!columns){ 
            columns = '^#WORKSPACE.columns';
            sourceNode.registerDynAttr('columns');
        }
        sourceNode.attr.columns = columns;
        var columns_bag = this._getColumnsBag(sourceNode,columns,subTagItems['column']);
        if(columns_bag.len()==0){
            gnrwdg.guessColumns = gnrwdg.guessColumns || '*';
        }
        if(gnrwdg.guessColumns){
            gnrwdg.columns_extra = {};
            columns_bag.forEach(function(n){
                gnrwdg.columns_extra[n.attr.field] = n.attr;
            });
            columns_bag = new gnr.GnrBag();
        }
        sourceNode.setAttributeInDatasource('columns',columns_bag);
        var default_kwargs = objectExtract(kw,'default_*');
        if(default_kwargs){
            kw.gridEditorPars = {default_kwargs:function(){
                return sourceNode.evaluateOnNode(default_kwargs);
            }};
        }
        var selected_kwargs = objectExtract(kw,'selected_*',true,true);
        if(kw.selectedId){
            kw.selectedId = sourceNode.absDatapath(kw.selectedId);
        }
        for(var k in selected_kwargs){
            selected_kwargs[k] = sourceNode.absDatapath(selected_kwargs[k])
        }
        objectUpdate(kw,selected_kwargs);


        var valuepath = value?sourceNode.absDatapath(value):null;
        dynamicStorepath = dynamicStorepath?'^'+sourceNode.absDatapath(dynamicStorepath):null;
        var store_kwargs = objectExtract(kw,'store_*');
        kw.nodeId = kw.nodeId || '_qg_'+genro.getCounter();
        kw.store = kw.nodeId;
        kw.datamode= kw.datamode || 'bag';
        kw.structpath = kw.structpath || '#WORKSPACE.struct';
        kw.controllerPath = '#WORKSPACE.controllers';
        kw.frameTarget = kw.frameTarget===false?false:true;
        kw.selfsubscribe_addrow= kw.selfsubscribe_addrow || '$1 = $1 || {}; this.widget.addRows($1._askResult? [$1._askResult]:$1._counter,$1.evt);';
        kw.selfsubscribe_delrow= kw.selfsubscribe_delrow || 'this.widget.deleteSelectedRows();';
        kw.selfsubscribe_export= kw.selfsubscribe_export || function(kwargs){
            this.widget.serverAction({command:"export", opt:{rawData:true,
                                                               export_mode:kwargs.export_mode ,
                                                               downloadAs:kwargs.downloadAs || 'export_'+genro.getCounter()}
                                        });     
        } ;
        kw.selfsubscribe_duprow= kw.selfsubscribe_duprow || 'this.widget.addRows($1._counter,$1.evt,true);';

        var currentValue = sourceNode.getAttributeFromDatasource('value');
        var currentColumns = sourceNode.getAttributeFromDatasource('columns');
        var struct = new gnr.GnrBag();
        sourceNode.setRelativeData(kw.structpath,struct)
        if(dynamicStorepath){
            kw.dynamicStorepath = dynamicStorepath;
            valuepath = '.dummystore';
        }
        sourceNode._('BagStore',objectUpdate({storepath:valuepath,
                        nodeId:kw.nodeId+'_store',datapath:kw.controllerPath,
                        storeType:kw.datamode=='bag'?'ValuesBagRows':'AttributesBagRows'},store_kwargs));
        var tools = subTagItems.tools;
        var gridRoot= tools.len()? this.toolsGridRoot(sourceNode,kw,tools.getAttr('#0')) : sourceNode;
        kw.datapath = kw.controllerPath;
        kw.gridplugins = false;
        var grid = gridRoot._('newIncludedView',kw);
        gnrwdg.gridNode = grid.getParentNode();
        gnrwdg.setColumns(sourceNode.getRelativeData(columns));
        return grid;
    },

    _getColumnsBag:function(sourceNode,columns,childrenColumns){
        var columns_bag = sourceNode.getRelativeData(columns) || new gnr.GnrBag();;
        childrenColumns.forEach(function(n){
            var attr = n.attr;
            attr.field = attr.field || n.label;
            columns_bag.setItem(attr.field,null,attr);
        })
        return columns_bag;
    },

    toolsGridRoot:function(sourceNode,kw,tools_kw){
        var tools = objectPop(tools_kw,'tools');
        tools_kw = tools_kw || {};
        var tools_bar_class,container_class;
        if(tools_kw.title){
            tools_bar_class = 'slotbar_toolbar_standard';
            tools_kw.position = 'TR';
        }
        var bckw = {height: objectPop(kw,'height'),
            width: objectPop(kw,'width'),_class:'quickgrid_container'}
        
        objectUpdate(tools_kw,objectExtract(kw,'tools_*'));
        var custom_tools = objectPop(tools_kw,'custom_tools');
        var default_tools={ 'addrow': {content_class:'iconbox add_row',_delay:500},
                            'delrow':{content_class:'iconbox delete_row'}, 
                            'duprow': {content_class:'iconbox copy'}, 
                            'export': {content_class:'iconbox export',
                                                 export_mode:'xls',
                                                 downloadAs:'',
                                                 localized_data:true,
                                                 ask:{title:'Export selection',skipOn:'Shift',
                                                 fields:[{name:'downloadAs',lbl:'Download as'},
                                                          {name:'allRows',label:'All rows',wdg:'checkbox'},
                                                         {name:'export_mode',wdg:'filteringSelect',values:'xls:Excel,csv:CSV',lbl:'Mode'},
                                                         {name:'localized_data',wdg:'checkbox',label:'Localized data'}]
                                             }}
                           }
        if(custom_tools){
            objectUpdate(default_tools,custom_tools);
        }
        tools=tools==true? 'addrow,delrow' : tools;
        var tools_position = objectPop(tools_kw,'position') || 'TR';
        var tool_region=(tools_position[0]=='T') ? 'top':'bottom';

        var centerkw = {region:'center',border:objectPop(kw,'border'),overflow:'hidden'};
        var bc = sourceNode._('borderContainer',bckw);
        
        var tpane = bc._('contentPane',{region:tool_region,height:'22px',overflow:'hidden',datapath:'#WORKSPACE.tools',
                                        _class:tools_bar_class});
        if(tools_kw.title){
            tpane._('div',{innerHTML:tools_kw.title,position:'absolute',left:'5px',top:'3px',
                        font_weight:'bold',font_size:'.9em',color:'#444'});
        }
        var posdict = {'TR':{right:'0',_class:'quickgrid_toolsbox_top quickgrid_toolsbox'},
                       'TL':{left:'0',_class:'quickgrid_toolsbox_top quickgrid_toolsbox'},
                        'BR':{right:'0',_class:'quickgrid_toolsbox_bottom quickgrid_toolsbox'},
                        'BL':{left:'0',_class:'quickgrid_toolsbox_bottom quickgrid_toolsbox'}}   
        var mb = tpane._('div',objectUpdate(posdict[tools_position],{position:'absolute'}))._('multibutton',{value:'^.command',sticky:false});
        tools.split(',').forEach(function(t){
            mb._('item',t,default_tools[t]);
        });
        tpane._('datacontroller',{script:"genro.publish({topic:value.action,nodeId:target},value)",
                                 value:'^.command',target:kw.nodeId})
        return bc._('contentPane',centerkw)
    },
    gnrwdg_guessDtypeAndWidth:function(rows,fields){
        var types={}
        var sizes={}
        var w,dtype,v
        if(!rows || rows.len()==0){
            return {types:null,sizes:null};
        }
        var store = this.gridNode.widget.collectionStore();
        if(!fields || fields=='*'){
            var firstNode = store.getData().getNode('#0');
            var nodeValue = firstNode.getValue();
            fields = nodeValue? nodeValue.keys():objectKeys(firstNode.attr);
        }else{
            fields = fields.split(',');
        }
        var infoInCellAttributes = this.infoInCellAttributes;
        var columns_extra = this.columns_extra || {};
        rows.forEach(function(n){
            var r = store.rowFromItem(n);
            fields.forEach(function(field){
                var v = r[field];
                if (!(field in types)){
                    types[field]=null
                    sizes[field]=0
                    if(infoInCellAttributes){
                        columns_extra[field] = n.getValue().getAttr(field);
                    }
                }
                if(!isNullOrBlank(v)){
                    dtype=types[field]
                    if (!dtype) {
                        dtype=guessDtype(v)
                        types[field]=dtype;
                    }   
                    w = 8 
                    if (dtype=='D'){w = 8}
                    else if (dtype=='H'){w = 6}
                    else if (dtype=='DH'){w = 12}
                    if ((dtype=='T') || (dtype=='N')|| (dtype=='L')){
                        sizes[field]=Math.max(sizes[field]||field.length,v.toString().length)
                    }
                    else if (sizes[field]==0){
                        w=8;
                        if (dtype=='D'){w = 8}
                        else if (dtype=='H'){w = 6}
                        else if (dtype=='DH'){w = 12}
                        sizes[field]=Math.max(field.length,w)
                    }
                }
            })
        })
        for (var t in types){
            if(!types[t]){types[t]='T'}
            sizes[t]=(2 +(sizes[t]|| 8)*.5)+'em'
        }
        if(objectNotEmpty(columns_extra)){
            this.columns_extra = columns_extra;
        }
        return {types:types,sizes:sizes}
    },
    gnrwdg_setFields:function(fields){
        var columns = this.getColumnsFromValue(this.gridNode.widget.storebag());
        this.setColumns(columns);
    },
    gnrwdg_getColumnsFromValue:function(value){
        var columns = new gnr.GnrBag();
        var columns_extra = this.columns_extra || {};
        var fields= this.sourceNode.getAttributeFromDatasource('fields');
        var guess = this.guessDtypeAndWidth(value, fields);
        var kw;
        for (var label in guess.types){
            kw = {'field':label,'dtype':guess.types[label],
                                         'width':guess.sizes[label],
                                          'name':stringCapitalize(label.replace(/_/g,' '))
                                      }
            if(label in columns_extra){
                var customColumn = columns_extra[label];
                if(customColumn){
                    objectUpdate(kw,customColumn);
                }
            }
            columns.setItem(label,null,kw);
        }
        return columns;
    },
    gnrwdg_catch_column:function(attr,value){
        this.setColumns(this.getColumnsFromValue(this.gridNode.widget.storebag()));
    },

    gnrwdg_setColumns:function(columns){
        this.gridNode.getRelativeData(this.gridNode.attr.structpath).setItem('view_0.rows_0',columns);
    },

    gnrwdg_setValue:function(value,kw,trigger_reason){
        if((trigger_reason=='container') || (kw.node.parentshipLevel(this.gridNode.widget.storebag().getParentNode())==0)){
            if(this.guessColumns){
                this.sourceNode.setRelativeData(this.sourceNode.attr.columns,this.getColumnsFromValue(value));
            }
        }
    }

});

dojo.declare("gnr.widgets.BagEditor", gnr.widgets.gnrwdg, {
    createContent:function(sourceNode,kw){
        var gnrwdg = sourceNode.gnrwdg;
        var selectedBranch = kw.selectedBranch || '#WORKSPACE.selectedBranch';
        var treekw = objectExtract(kw,'storepath,labelAttribute');
        var barkw = objectExtract(kw,'addrow,delrow,addcol,searchOn,export');
        sourceNode.attr._workspace = true;
        objectUpdate(treekw,{hideValues:true,selectedLabelClass:'selectedTreeNode',_class:"branchtree noIcon",autoCollapse:true});
        objectUpdate(treekw,objectExtract(kw,'tree_*'));
        treekw.selectedPath =  selectedBranch;
        var that = this;
        treekw.selfsubscribe_onSelected = function(kw){
            var rows = this.getRelativeData(this.attr.storepath).getItem(kw.path);
            that.onSelectedBranch(rows,gnrwdg.gridNode);
        }

        var bc = sourceNode._('BorderContainer');
        var treepane = bc._('ContentPane',{region:'left',width:objectPop(treekw,'width') || '200px',splitter:true,
                                            border_right:'1px solid #efefef',background:'#EBEBEB'})._('div',{position:'absolute',top:'1px',left:'1px',right:'1px',bottom:'1px',overflow:'auto'})
        var tree = treepane._('tree',treekw);
        gnrwdg.treeNode = tree.getParentNode();
        var frameCode = 'bagEditor_'+ genro.getCounter();
        var gridId = frameCode+'_grid';
        var gridframe = bc._('framePane',{frameCode:frameCode,region:'center',target:gridId,margin_left:'4px'});
        if(objectNotEmpty(barkw)){
            var slots = '*,'+['delrow','addrow','addcol','export','searchOn'].filter(function(n){return n in barkw}).join(',')+',5';
            var bar = gridframe._('SlotBar',{'side':'top',slots:slots,toolbar:true});
            if(barkw.delrow){
                bar._('SlotButton','delrow',{label:_T('Delete row'),publish:'delrow',iconClass:'iconbox delete_row'});
            }
            if(barkw.addrow){
                bar._('SlotButton','addrow',{label:_T('Add row'),publish:'addrow',iconClass:'iconbox add_row'});
            }
            if(barkw.addcol){
                bar._('SlotButton','addcol',{label:_T('Add column'),publish:'addcol'});
            }
            if(barkw.export){
                bar._('SlotButton','export',{iconClass:'iconbox export',
                                                 opt_export_mode:'xls',
                                                 opt_downloadAs:'',
                                                 opt_localized_data:true,
                                                 publish:'serverAction',command:'export',
                                                 ask:{title:'Export selection',skipOn:'Shift',
                                                 fields:[{name:'opt_downloadAs',lbl:'Download as'},
                                                          {name:'opt_allRows',label:'All rows',wdg:'checkbox'},
                                                         {name:'opt_export_mode',wdg:'filteringSelect',values:'xls:Excel,csv:CSV',lbl:'Mode'},
                                                         {name:'opt_localized_data',wdg:'checkbox',label:'Localized data'}]
                                             }
                                         })
            }
        }
        var gridkw = objectExtract(kw,'grid_*');
        gridkw.nodeId = gridId;
        gridkw.frameCode = frameCode;
        gridkw.selfDragRows = true;
        gridkw.datapath = '#WORKSPACE.grid';
        var branchPath = kw.branchPath || '#WORKSPACE.branchBag';
        gridkw.controllerPath = gridkw.datapath;
        gridkw.structpath = '#WORKSPACE.grid.struct';
        gridkw.store = frameCode;
        gridkw.selfsubscribe_delrow = function(){
            this.widget.deleteSelectedRows();
        };
        gridkw.selfsubscribe_addrow = function(){
            var that = this;
            genro.dlg.prompt(_T('Add row'),{lbl:'Nodelabel',action:function(result){
                    var b = that.widget.storebag();
                    b.setItem(result,new gnr.GnrBag({nodelabel:result}));
                }});
        }
        gridkw.selfsubscribe_addcol = function(){
            var that = this;
            genro.dlg.prompt(_T('Add col'),{'widget':[{lbl:'name',value:'^.field'},
                                             {lbl:'dtype',value:'^.dtype',wdg:'filteringSelect',values:'T:Text,N:Number,B:Boolean'}],
                                        action:function(result){
                                                    var b = genro.getData(that.attrDatapath('structpath'));
                                                    var kw = result.asDict();
                                                    kw.name = kw.field;
                                                    kw.edit = true;
                                                    b.setItem('#0.#0.cell_'+genro.getCounter(),null,kw);
                                                }
                                        });
        }

        gridframe._('BagStore',{storepath:branchPath,_identifier:'nodelabel',nodeId:frameCode+'_store'});
        var grid = gridframe._('newIncludedView',gridkw);
        gnrwdg.gridNode = grid.getParentNode();
        sourceNode._('dataController',{'script':"this.getParentNode().gnrwdg.updateBranchBag(branch,_node,_reason,_triggerpars.kw);",branch:'^'+branchPath});

        return bc;

    },
    onSelectedBranch:function(rows,gridNode){        
        var struct = new gnr.GnrBag();
        var header = new gnr.GnrBag();
        struct.setItem('view_0.rows_0',header);
        var store = new gnr.GnrBag();
        var i = 0;
        var f;
        header.setItem('cell_0',null,{field:'nodelabel',width:'12em',name:'Node Label'});
        if(rows && rows.len && rows.len()){
            rows._nodes.forEach(function(n,idx){
                    var attr = objectUpdate({},n.attr);
                    for(var k in attr){
                        f = k.replace(/\W/g, '_');
                        attr[f] = objectPop(attr,k);
                        if(!header.getNodeByAttr('field',f)){
                            header.setItem('cell_'+genro.getCounter(),null,{field:f,width:'10em',name:f,dtype:guessDtype(attr[f]),original_field:k,edit:true});
                        }
                    }
                    attr.nodelabel = n.label;
                    store.setItem('r_'+idx,new gnr.GnrBag(attr));
                    i++;
                },'static');
        }
        gridNode.setRelativeData(gridNode.attr.structpath,struct);
        gridNode.setRelativeData(gridNode.attr.storepath,store);
    },
    gnrwdg_updateBranchBag:function(branch,branchNode,reason,kw){
        var b = this.treeNode.getRelativeData(this.treeNode.attr.storepath).getItem(this.treeNode.getRelativeData(this.treeNode.attr.selectedPath));
        var nv = branchNode.getValue();
        if(reason=='child'){
            if(kw.updvalue){
                var nl = branchNode.getParentNode().label;
                var updkw = {};
                updkw[branchNode.label] = kw.value;
                b.getNode(nl).updAttributes(updkw);
            }else if(kw.evt=='ins' && nv instanceof gnr.GnrBag){
                var pos = branch.index(branchNode.label);
                b.setItem(branchNode.label,null,nv.asDict(),{_position:pos>=0?pos:null});
            }else if(kw.evt=='del' && nv instanceof gnr.GnrBag){
                b.popNode(branchNode.label);
            }
        }
    }
});

dojo.declare("gnr.widgets.PagedHtml", gnr.widgets.gnrwdg, {
    createContent:function(sourceNode,kw){
        var pagingKw = objectExtract(kw,'sourceText,pagedText,letterheads,extra_bottom,printAction,bodyStyle,editor,datasource,letterhead_id');
        kw['height'] = '100%';
        kw['position'] = 'relative';
        kw['background'] = 'white';
        kw['_workspace'] = true;
        var gnrwdg = sourceNode.gnrwdg;
        gnrwdg.datasource = pagingKw.datasource;
        gnrwdg.tpl_kwargs = objectExtract(kw,'tpl_*',false,true);
        gnrwdg.extra_bottom = pagingKw.extra_bottom || 10;
        gnrwdg.pagedTextPath = pagingKw.pagedText.replace('^','');
        gnrwdg.letterheadsPath = pagingKw.letterheads.replace('^','');
        gnrwdg.sourceTextPath = pagingKw.sourceText.replace('^','');
        if(pagingKw.editor){
            gnrwdg.editorNode = sourceNode.currentFromDatasource(pagingKw.editor);
        }
        sourceNode.attr.sourceText = pagingKw.sourceText;
        sourceNode.attr.letterheads = pagingKw.letterheads;
        sourceNode.attr.letterhead_id = pagingKw.letterhead_id;

        sourceNode.subscribe('paginate',function(){
            gnrwdg.paginate();
        });

        kw['style'] = pagingKw.bodyStyle;
        var container = sourceNode._('div',kw);
        var top = container._('div',{position:'absolute',top:'0',left:0,right:0,height:'20px',gradient_from:'silver',gradient_to:'whitesmoke',gradient_deg:-90,border_bottom:'1px solid silver'})
        top._('horizontalSlider',{value:'^#WORKSPACE.zoom','default':0.3,minimum:0.3, maximum:1,intermediateChanges:true, width:'15em',margin_top:'2px'})
        if(pagingKw.printAction){
            top._('div',{_class:'iconbox print',connect_onclick:pagingKw.printAction,position:'absolute',right:'2px',top:'0px'})
        }
        var b = container._('div',{position:'absolute',top:'20px',left:0,bottom:0,right:0});
        var rootKw = {innerHTML:pagingKw.pagedText,position:'absolute',top:'0',left:0,right:0,bottom:0,zoom:'^#WORKSPACE.zoom',
                                      overflow:'auto',_class:'pe_preview_box'};
        rootKw.connect_onclick = function(evt){
            gnrwdg.onClick(evt);
        }
        gnrwdg.pagesRoot = b._('div',rootKw).getParentNode();
        return container;
    },
    gnrwdg_onClick:function(evt){
        var target = evt.target;
        while(target && target.getAttribute && !target.getAttribute('orig_idx')){
            target = target.parentNode;
        }
        if(target && target.getAttribute && target.getAttribute('orig_idx')){
            var c=parseInt(target.getAttribute('orig_idx'));
        }else{
            var c=-1;
        }
        if(this.editorNode){
            this.editorNode.externalWidget.gnr_highlightChild(c);
        }
    },

   //gnrwdg_setLetterheads:function(letterheads){
   //    this.paginate();
   //},

    gnrwdg_setLetterhead_id:function(letterhead_id,kw,reason){
        if(reason=='container'){
            return;
        }
        this.paginate();
    },

    gnrwdg_addPage:function(){
        var rn = this.pagesRoot.domNode;  
        var p = document.createElement('div'); 
        var content_node;  
        var letterheads = this.sourceNode.getRelativeData(this.letterheadsPath);    
        if(letterheads){
            var lnumber = rn.childElementCount;
            var max_lnumber = letterheads.len()-1;
            if(lnumber>max_lnumber){
                lnumber = max_lnumber;
            }
            var letterhead_page = letterheads.getItem('#'+lnumber);
            this.sourceBag.setItem('p',rn.childElementCount+1);
            p.innerHTML = dataTemplate(letterhead_page,this.sourceBag,null,true);
            var p = p.children[0];
            content_node = dojo.query('div[content_node=t]',p)[0];
        }else{
            genro.dom.addClass(p,'pe_pages');
            content_node = p;
        }
        rn.appendChild(p);
        genro.dom.addClass(content_node,'pe_content')
        return content_node;
    },

    gnrwdg_setSourceText:function(value,kw,trigger_reason){    
        if(trigger_reason!='container'){
            this.paginate();
        }
    },

    gnrwdg_onPaginating:function(){
        var pagesDomNode = this.pagesRoot.domNode;
        this.pagesDomNodeParent = pagesDomNode.parentNode;
        dojo.body().appendChild(pagesDomNode);
        var sn = this.sourceNode;
        this.sourceBag = sn.getRelativeData(this.datasource).deepCopy();
        this.sourceBag.setItem('pp','#PP');
        for(var k in this.tpl_kwargs){
            this.sourceBag.setItem(k,sn.currentFromDatasource(this.tpl_kwargs[k]));
        }
        pagesDomNode.style.visibility ='hidden';
        this.currentZoom = pagesDomNode.style.zoom ;
        pagesDomNode.style.zoom ='1';
    },

    gnrwdg_onPaginated:function(){
        var pagesDomNode = this.pagesRoot.domNode;
        this.pagesDomNodeParent.appendChild(pagesDomNode)
        pagesDomNode.innerHTML = pagesDomNode.innerHTML.replace(/\#PP/g, pagesDomNode.childElementCount);
        pagesDomNode.style.zoom = this.currentZoom;
        pagesDomNode.style.visibility ='visible';
    },

    gnrwdg_paginate:function(){
        var sourceHtml = this.sourceNode.getRelativeData(this.sourceTextPath);
        var pagesDomNode = this.pagesRoot.domNode;
        pagesDomNode.innerHTML = '';
        if(sourceHtml){
            this.onPaginating();
            var page = this.addPage();
            var dest = document.createElement('div');
            page.appendChild(dest);
            var src = document.createElement('div'); 
            src.innerHTML = sourceHtml;
            var children = src.children;
            var node;
            var idx = 0;
            while(children.length){
                node = src.removeChild(children[0]);
                node.setAttribute('orig_idx',idx);
                genro.dom.addClass(node,'pe_node');
                dest.appendChild(node);                
                if((dest.clientHeight+this.extra_bottom>=page.clientHeight) || (node.innerHTML.indexOf('--//--')>=0)){
                    node = dest.removeChild(node);
                    page = this.addPage();
                    dest = document.createElement('div');
                    page.appendChild(dest);
                    if(node.innerHTML.indexOf('--//--')<0){
                        dest.appendChild(node);
                    }
                }
                idx++;
            }
            this.onPaginated();
        }
        
        this.sourceNode.setRelativeData(this.pagedTextPath,pagesDomNode.innerHTML,null,null,this.pagesRoot);
    }
});

dojo.declare("gnr.widgets.TemplateChunk", gnr.widgets.gnrwdg, {
    getVirtualColumns:function(tpl_vc,curr_vc){
        curr_vc = curr_vc?curr_vc.split(','):[]
        tpl_vc = tpl_vc? tpl_vc.split(','):[];
        if(!curr_vc){
            curr_vc = tpl_vc;
        }else{
            dojo.forEach(tpl_vc,function(c){
                if(dojo.indexOf(curr_vc,c)<0){
                    curr_vc.push(c)
                }
            });
        }
        return curr_vc;
    },

    loadTemplateEditData:function(sourceNode){
        var paletteNode = sourceNode._connectedPalette;
        var templateHandler = sourceNode._templateHandler;
        paletteNode.setRelativeData('.data',templateHandler.data?templateHandler.data.deepCopy():new gnr.GnrBag()); 
        var respath = templateHandler.dataInfo.respath;
        if(respath && respath.indexOf('_custom')>=0){
            paletteNode.setRelativeData('.data.metadata.custom',true);
        }
    },
    gnrwdg_setTemplate:function(templateBag){
        if(this.chunkNode._connectedPalette){
            this.gnr.loadTemplateEditData(this.chunkNode);
        }
    },
    
    openTemplatePalette:function(sourceNode,editorConstrain,showLetterhead){
        var paletteCode = 'template_editor_'+sourceNode._id;
        //genro._data.popNode('gnr.palettes.'+paletteCode);
        var tplpars = sourceNode.attr._tplpars;
        var templateHandler = sourceNode._templateHandler;
        var handler = this;
        var paletteId = paletteCode+'_floating';

        if(sourceNode._connectedPalette){
            var paletteNode = sourceNode._connectedPalette;
            paletteNode.getWidget().show();
        }else{
            var table = tplpars.table;
            var remote_datasourcepath =  sourceNode.absDatapath(sourceNode.attr.datasource);
            var showLetterhead = typeof(showLetterhead)=='string'?(sourceNode.getRelativeData(showLetterhead) || true):showLetterhead;
            var kw = {'paletteCode':paletteCode,'dockTo':'dommyDock:open',
                    title:'Template Edit '+table?table.split('.')[1]:'',width:'750px',
                    maxable:true,
                    height:'500px',
                    remote:'te_chunkEditorPane',
                    remote_table:table,
                    remote_paletteId:paletteId,
                    remote_resource_mode:!table || (templateHandler.dataInfo.respath!=null),
                    remote_datasourcepath:remote_datasourcepath,
                    remote_showLetterhead:showLetterhead,
                    remote_editorConstrain: editorConstrain
                    };  
            kw.remote__onRemote = function(){
                handler.loadTemplateEditData(sourceNode);
            }
            kw.palette_selfsubscribe_savechunk = function(){
                tplpars = sourceNode.evaluateOnNode(tplpars);
                var template = tplpars.template || new gnr.GnrBag();
                var data = this.getRelativeData('.data').deepCopy();
                var custom = data.pop('metadata.custom');
                if(typeof(template)=='string'){
                    var respath = handler.saveTemplate(sourceNode,data,tplpars,custom);
                    templateHandler.dataInfo.respath = respath;
                }else{
                    var tplpath = sourceNode.attr._tplpars.template;
                    var currdata = sourceNode.getRelativeData(tplpath,data) 
                    if(!currdata){
                        currdata = new gnr.GnrBag();
                        sourceNode.setRelativeData(tplpath,currdata)
                    }
                    currdata.clear();
                    data.forEach(function(n){currdata.setItem(n.label,n._value,n.attr)});
                }
                templateHandler.setNewData({data:data,template: data.getItem('compiled'),dataInfo:templateHandler.dataInfo});           
                sourceNode.updateTemplate();
                sourceNode.publish('onChunkEdit');
                this.widget.hide();
            }
            var palette = sourceNode._('palettePane',kw);
            var paletteNode = palette.getParentNode();  
            sourceNode._connectedPalette = paletteNode; 
        }
    },
    

    updateVirtualColumns:function(sourceNode,datasourceNode,dataProvider,mainNode){
        var vc,curr_vc;
        if(dataProvider){
            curr_vc = dataProvider.attr.virtual_columns
            vc = this.getVirtualColumns(mainNode.attr.virtual_columns,curr_vc);
            if(vc){
                dataProvider.attr.virtual_columns = vc.join(',');
                dataProvider.fireNode();
            }
        }else{
            curr_vc = datasourceNode.attr._virtual_columns;
            vc = this.getVirtualColumns(mainNode.attr.virtual_columns,curr_vc);
            if(vc){
                if(datasourceNode._resolver){
                    datasourceNode._resolver.kwargs.virtual_columns = vc.join(',');
                    datasourceNode._resolver.lastUpdate = null;                    
                    sourceNode.attr._virtual_column = dojo.map(vc,function(c){return datasourceNode.label+'.'+c;}).join(',');
                }else{
                    sourceNode.attr._virtual_column =  vc.join(',');
                }
            }
        }
    },
    
    loadTemplate:function(sourceNode,kw){
        kw.template = kw.template || new gnr.GnrBag();
        if(kw.template instanceof gnr.GnrBag){
            var data = kw.template;
            return {data:data,dataInfo:{},template:data.getItem('compiled')};
        }
        var template_address =( kw.table || '')+':'+kw.template;
        var result = genro.serverCall("loadTemplate",{template_address:template_address,asSource:kw.asSource});
        if(result.attr.html){
            var content = result.getValue().getItem('content');
             return {template:content,dataInfo:result.attr,data:new gnr.GnrBag({'content':content})};
        }
        if(kw.asSource){
            var data = result.getValue();
            return {data:data,dataInfo:result.attr,template:data instanceof gnr.GnrBag?data.getItem('compiled'):''};
        }
        return {template:result};
    },
    
    saveTemplate:function(sourceNode,data,kw,custom){
        var template_address = (kw.table || '')+':'+kw.template;
        var templateHandler = sourceNode._templateHandler;
        if(custom){
            template_address = template_address+',custom'
        }
        return genro.serverCall("saveTemplate",{template_address:template_address,data:data},null,null,'POST');
    },
    
    
    createContent:function(sourceNode, kw,children) {
        var resource = objectPop(kw,'resource');
        if(resource){
            console.warn('templateChunk warning: use "template" param instead of "resource" param');
        }
        var tplpars = objectExtract(kw,'table,template,editable');
        tplpars.table = tplpars.table || '';
        var editorConstrain = objectExtract(kw,'constrain_*',null,true);
        var showLetterhead = objectPop(kw, 'showLetterhead');
        if(typeof(showLetterhead)=='string'){
            showLetterhead = sourceNode.absDatapath(showLetterhead);
        }
        var record_id = objectPop(kw, 'record_id');
        genro.assert((record_id || kw.datasource),'record_id or datasource are mandatory in templatechunk');

        if(record_id){
            sourceNode.attr.record_id = record_id;
        }
        sourceNode.attr.template = tplpars.template;
        for(var k in editorConstrain){
            var c = editorConstrain[k];
            if(typeof(c)=='string' && (c[0]=='^' || c[0]=='=')){
                editorConstrain[k] = c[0]+sourceNode.absDatapath(c);
            }
        }
        var showAlways = tplpars.editable;
        tplpars.template = tplpars.template || resource;
        kw._tplpars = tplpars;
        kw._tplpars.editable = kw._tplpars.editable || (genro.isDeveloper? 'developer':false);
        kw._tplpars.showAlways = kw._tplpars.editable===true;
        kw._tplpars.asSource =  kw._tplpars.editable!=null;
        kw._class = (kw._class || '') + ' selectable'
        var dataProvider = objectPop(kw,'dataProvider');
        if(dataProvider){
            dataProvider = sourceNode.currentFromDatasource(dataProvider);
        }
        
        var handler = this;
        if(tplpars.editable){
            kw.selfsubscribe_openTemplatePalette = function(){
                handler.openTemplatePalette(this,editorConstrain,showLetterhead);
            }
            kw.connect_ondblclick = function(evt){
                if(tplpars.editable==true || evt.shiftKey){
                    handler.openTemplatePalette(this,editorConstrain,showLetterhead);
                }
           };
        }
        kw.onCreated = function(domnode,attributes){
            this._templateHandler = {};
            var templateHandler=this._templateHandler
            templateHandler.showAlways = showAlways;
            if(record_id){
                handler.createServerChunk(this,record_id,tplpars);
            }
            else{
                handler.createClientChunk(this,dataProvider,tplpars);
            }
            //this.updateTemplate(); to check
        }
        var chunk = sourceNode._('div','templateChunk',kw)
        sourceNode.gnrwdg.chunkNode = chunk.getParentNode();
        return chunk;
    },



    createClientChunk:function(sourceNode,dataProvider,tplpars){
        var templateHandler = sourceNode._templateHandler;
        var cls = this;
        templateHandler.cb = function(){
            this.setNewData(cls.loadTemplate(sourceNode,sourceNode.evaluateOnNode(tplpars))); 
        };   
        templateHandler.setNewData= function(result){
            this.data = result.data;
            this.dataInfo = result.dataInfo;
            this.template = result.template;
            this.defaults = {};
            var datasourcePath = sourceNode.absDatapath(sourceNode.attr.datasource);
            var datasourceNode = genro.getDataNode(datasourcePath);
            if(this.template instanceof gnr.GnrBag){
                 var varsbag = this.data.getItem('varsbag');
                 var defaults = this.defaults;
                 if(varsbag){
                     varsbag.forEach(function(n){
                         var v = n.getValue();
                         defaults[v.getItem('fieldpath')] = '<span class="chunkeditor_varplaceholder">'+(v.getItem('fieldname')||'')+'</span>';
                         },'static');
                }
                var mainNode = this.template.getNode('main');
                cls.updateVirtualColumns(sourceNode,datasourceNode,dataProvider,mainNode)  
            }else{
                this.template = this.template || '<div class="chunkeditor_emptytemplate">Template not yet created</div>';
            }
        };
        sourceNode.updateTemplate = function(){
            this._templateHandler.template = null;
            var result = dataTemplate(this._templateHandler, this, this.attr.datasource);
            if(this.isPointerPath(this.attr.innerHTML)){
                this.setRelativeData(this.attr.innerHTML,result);
            }else{
                this.domNode.innerHTML = result;
            }
        }
        sourceNode.attr.template = templateHandler;
        sourceNode._('dataController',{'script':"this.getParentBag().getParentNode().updateTemplate();",_fired:tplpars.template});
    },

    createServerChunk:function(sourceNode,record_id,tplpars){
        var templateHandler = sourceNode._templateHandler;
        sourceNode.updateTemplate = function(pkey){
            var that = this;
            if(pkey){
                genro.serverCall('te_renderChunk',{record_id:pkey,template_address:tplpars.table+':'+tplpars.template,_sourceNode:sourceNode},function(resultNode){
                    var r = resultNode.getValue();
                    templateHandler.dataInfo = resultNode.attr;
                    if(r instanceof gnr.GnrBag){
                        that.domNode.innerHTML = r.getItem('rendered');
                        templateHandler.data = r.popNode('template_data').getValue();
                    }else{
                        that.domNode.innerHTML = r;
                        templateHandler.data = new gnr.GnrBag();
                    }
                    
                },null,'POST');
            }else{
                sourceNode.domNode.innerHTML = '';
                templateHandler.dataInfo = {};
                templateHandler.data = new gnr.GnrBag();
            }
        }
        templateHandler.setNewData = function(result){
            sourceNode.updateTemplate(sourceNode.getRelativeData(record_id));
        }
        sourceNode.registerSubscription('changeInTable',sourceNode,function(kw){
            var mainNode = this.getParentNode();
            var currpkey = mainNode.getAttributeFromDatasource('record_id');
            if(kw.table==this.attr._tplpars.table && currpkey==kw.pkey){
                mainNode.gnrwdg.refresh();
            }
        });
        //sourceNode._('dataController',{'script':"this.getParentBag().getParentNode().updateTemplate(pkey);",pkey:record_id});
    },
    gnrwdg_refresh:function(){
        var pkey;
        var tnode = this.sourceNode._value.getNode('templateChunk');

        if(this.sourceNode.attr.record_id){
            pkey = this.sourceNode.getAttributeFromDatasource('record_id');
        }
        tnode.updateTemplate(pkey);
    },
    gnrwdg_setRecord_id:function(pkey){
        var tnode = this.sourceNode._value.getNode('templateChunk');
        tnode.updateTemplate(pkey);
    }
});

dojo.declare("gnr.widgets.DropUploaderGrid", gnr.widgets.gnrwdg, {
    createContent:function(sourceNode, kw,children) {
        var uploaderPars = objectExtract(kw,'onUploadedMethod,onUploadingMethod');
        var uploaderKw = objectExtract(kw,'uploadPath,filename,onResult,onError,onProgress,onAbort');
        objectUpdate(uploaderPars,objectExtract(kw,'rpc_*'));
        var nodeId = objectPop(kw,'nodeId') || 'uploader_'+genro.getCounter()
        uploaderKw.uploadPath = uploaderKw.uploadPath || 'page:'+nodeId;
        var label = objectPop(kw,'label');
        var containerKw = objectExtract(kw,'position,top,left,right,bottom,height,width,border,rounded,_class,style,region');
        var rootbc = sourceNode._('bordercontainer',containerKw);
        
        var grid = rootbc._('contentPane',{'region':'center'})._('quickGrid',{value:kw.storepath || '^gnr.uploadedFiles',
                                        nodeId:nodeId,
                                        dropTarget_grid:'Files',
                                        dropTypes:'Files',
                                        selfsubscribe_doUpload:function(){
                                            
                                            genro.rpc.uploadMultipartFiles(this.widget.storebag(),
                                                                    {onResult:funcCreate(uploaderKw.onResult,'result',this),
                                                                    uploadPath:uploaderKw.uploadPath,uploaderId:nodeId});
                                        },
                                        onDrop:function(dropInfo,files){
                                            var filebag = this.widget.storebag();
                                            files.forEach(function(f){
                                                let row = {_name:f.name,_size:f.size,_type:f.type,_file:f,_uploaderId:nodeId};
                                                let label = (f.name+'_'+f.size+'_'+f.type).replace(/\W/g,'_');
                                                if(filebag.index(label)<0){
                                                    filebag.addItem(label,new gnr.GnrBag(row));
                                                }
                                            });
                                        }});
        grid._('column',{name:_T('Filename'),field:'_name',width:'15em',edit:true});
        grid._('column',{name:_T('Size'),field:'_size',width:'5em','dtype':'L'});
        grid._('column',{name:_T('Type'),field:'_type',width:'10em'});
        grid._('column',{name:_T('Status'),field:'_status',width:'10em'});
        grid._('tools',{tools:'delrow',title:label || _T('Drop here files to upload')});

        return rootbc;
    }
});

dojo.declare("gnr.widgets.DropUploader", gnr.widgets.gnrwdg, {
    createContent:function(sourceNode, kw,children) {
        var gnrwdg = sourceNode.gnrwdg;
        var uploaderPars = objectExtract(kw,'onUploadedMethod,onUploadingMethod');
        var uploaderKw = objectExtract(kw,'uploadPath,filename,onResult,onError,onProgress,onAbort');
        objectUpdate(uploaderPars,objectExtract(kw,'rpc_*'));
        var nodeId = objectPop(kw,'nodeId') || 'uploader_'+genro.getCounter()
        uploaderKw.uploadPath = uploaderKw.uploadPath || 'page:'+nodeId;
        var label = objectPop(kw,'label');
        var dropAreaKw = {nodeId:nodeId,dropTarget:objectPop(kw,'dropTarget',true),
                          dropTypes:objectPop(kw,'dropTypes','Files'),
                         _class:'dropUploaderBoxInner'};
        var containerKw = objectExtract(kw,'position,top,left,right,bottom,height,width,border,rounded,_class,style')

        gnrwdg.pendingHandlers = [];
        var uploadhandler_key = genro.isMobile? 'selfsubscribe_doubletap':'connect_ondblclick'
        dropAreaKw[uploadhandler_key] = function(){
            if(gnrwdg.pendingHandlers.length){
                genro.dlg.ask(_T("Abort upload"),
                 _T("Are you sure?"),null,{
                     confirm:function(){
                        gnrwdg.pendingHandlers.forEach(function(h){
                            if(h._progressDiv){
                                gnrwdg.rootNode.domNode.removeChild(h._progressDiv);
                            }
                            h.abort()
                        });
                        gnrwdg.pendingHandlers = [];
                    }
                 });
            }else{
                gnrwdg.fakeinputNode.domNode.click();
            }
        }
        dropAreaKw.innerHTML = dropAreaKw.innerHTML || label || '&nbsp;';
        var maxsize = objectPop(kw,'maxsize');
        uploaderKw.uploaderId = dropAreaKw.nodeId;  
        var onUploadingCb = objectPop(kw,'onUploadingCb') || function(){};
        onUploadingCb = funcCreate(onUploadingCb,'dropInfo,data',sourceNode);
        var progressBar = objectPop(kw,'progressBar',true);
        if(uploaderKw.onResult){
            uploaderKw.onResult = funcCreate(uploaderKw.onResult,'evt',sourceNode);
        }
        if(uploaderKw.onError){
            uploaderKw.onError = funcCreate(uploaderKw.onError,'evt',sourceNode);
        }
        if(uploaderKw.onAbort){
            uploaderKw.onAbort = funcCreate(uploaderKw.onAbort,'evt',sourceNode);
        }
        if(uploaderKw.onProgress){
            uploaderKw.onProgress = funcCreate(uploaderKw.onProgress,'evt',sourceNode);
        }else if(progressBar){
            uploaderKw.onProgress = function(evt){
                var d = evt._sender._progressDiv;
                if(d){
                    d.style.width = (evt.loaded *100) /evt.total +'%';
                    if(evt.loaded == evt.total){
                        gnrwdg.rootNode.domNode.removeChild(d);
                        gnrwdg.pendingHandlers.splice(evt._sender._counter,1);
                    }
                }
            };
        }
        var cbOnDropData = function(dropInfo,data){
            var doUpload = onUploadingCb(dropInfo,data);
            if(doUpload===false){
                return false;
            }
            return genro.rpc.uploadMultipart_oneFile(data,objectUpdate({},uploaderPars),objectUpdate({filename:data.name},uploaderKw));
        }
        var onFiles  = function(dropInfo,files){
            gnrwdg.pendingHandlers = [];
            if(sourceNode.form && sourceNode.form.isDisabled()){
                genro.dlg.alert("The form is locked",'Warning');
                return false;
            }
            var totSize = 0;
            if(maxsize){
                dojo.forEach(function(f){
                    totSize += f.size;
                });
                if (totSize>maxsize){
                    var size_kb = maxsize/1000
                    genro.dlg.alert("File exeeds size limit ("+size_kb+"KB)",'Error');
                    return false;
                }
            }
            var c = 0;
            var height = Math.round(100/files.length)
            dojo.forEach(files,function(f){
                var h = cbOnDropData(dropInfo,f);
                if(h){
                    gnrwdg.pendingHandlers.push(h);
                    if(progressBar){
                        var pb = document.createElement('div');
                        pb.style.position = 'absolute';
                        pb.style.top = c*height+'%';
                        pb.style.left = 0;
                        pb.style.height = height+'%';
                        pb.style.background = 'rgba(11,121,171,0.30)';
                        gnrwdg.rootNode.domNode.appendChild(pb);
                        h._counter = c;
                        h._progressDiv = pb;
                    }
                    c+=1;
                }
            });
        };
        dropAreaKw.onDrop = onFiles;
        containerKw._class =containerKw._class ||  'dropUploaderBox' ;
        var container = sourceNode._('div',containerKw);
        var fakeinput = container._('input',{hidden:true,
            type:'file',
                connect_onchange:function(evt){
                    onFiles({evt:evt},evt.target.files);
                    this.domNode.value = null;
                }
        });
        gnrwdg.fakeinputNode = fakeinput.getParentNode();
        container._('div',objectUpdate(dropAreaKw,kw))
        gnrwdg.rootNode = container.getParentNode();
        return container;
    }
});


dojo.declare("gnr.widgets.SlotButton", gnr.widgets.gnrwdg, {
    createContent:function(sourceNode, kw,children) {
        var inherithed=sourceNode.getInheritedAttributes();
        kw['showLabel'] = kw.iconClass? (kw['showLabel'] || false):true; 
        if (!kw['showLabel']){
            kw['_class']= kw['_class'] ? kw['_class']+' slotButtonIconOnly':' slotButtonIconOnly';
        }
        var targetNode,prefix;
        var tag = 'button';
        var target = objectPop(kw,'target') || inherithed.target;
        if(target!=false){
            if(target){
                targetNode = genro.nodeById(target,sourceNode);
                prefix = targetNode?(targetNode.attr.nodeId || targetNode.getStringId()):target;
            }else if(inherithed.frameCode){
                var framePane = genro.getFrameNode(inherithed.frameCode);
                if(framePane){
                    targetNode = framePane.getValue().getNodeByAttr('frameTarget',true);
                    if(targetNode){
                        prefix = targetNode.attr.nodeId || inherithed.frameCode+'_target';
                    }
                }
            }
        }else{
            prefix=inherithed.slotbarCode;
        }
        var publish=objectPop(kw,'publish');
        if(kw.menupath){
            kw['storepath'] = objectPop(kw,'menupath');
            tag = 'menudiv';
        }

        if(!kw.action && publish){
            kw.topic = prefix?prefix+'_'+publish:publish;
            kw.command = kw.command || null;
            //kw.opt = objectExtract(kw,'opt_*',true);
            if(tag=='button'){
                kw['action'] = "genro.publish(topic,{'command':command,modifiers:genro.dom.getEventModifiers(event),opt:objectExtract(_kwargs,'opt_*'),evt:event,_counter:_counter});";
            }else{
                kw['action'] = "objectPop($1,'caption');genro.publish('"+kw.topic+"',{'command':'"+(kw.command || '')+ "' ||null,modifiers:genro.dom.getEventModifiers(event),evt:event,opt:$1});";
            }
        }
        return sourceNode._(tag,kw);
        
    }

});

dojo.declare("gnr.widgets.DocItem", gnr.widgets.gnrwdg, {
    createContent:function(sourceNode, kw,children) {
        var _class = objectPop(kw,'_class');
        kw._class = _class? 'doc_item selectable ' +_class : 'doc_item selectable';
        var docpars = objectExtract(kw,'store,key,contentpath');
        kw._docKey = docpars.key;
        kw._docStore = docpars.store;
        kw._docContentPath = docpars.contentpath;
        kw.datapath = '==(_docStore && _docKey && _docContentPath)?"_doc.content."+_docStore+"."+_docKey+"."+_docContentPath:"_emptypath"';
        kw.connect_ondblclick = "genro.publish('editDocItem',{docItem:this});" 
        kw.connect_onclick = "genro.publish('focusDocItem',{docItem:this});"   
        return sourceNode._('div',kw)._('div', 
                    {innerHTML:'==(_allcontent&&_current_lang)?(_allcontent.getItem(_current_lang)?_allcontent.getItem(_current_lang):_allcontent.getItem("#0")):"";',
                            '_class':'^.?contentClasses','style':'^.?contentStyles',_current_lang:'^gnr.language',_allcontent:'^.'})
    }

});


dojo.declare("gnr.widgets.MultiButton", gnr.widgets.gnrwdg, {
    subtags:{'item':true,'store':true},
    createContent:function(sourceNode, kw,children,subTagItems) {
        var value = objectPop(kw,'value');
        var values = objectPop(kw,'values');
        var items = objectPop(kw,'items');
        var multibuttonstore = objectPop(subTagItems,'store');
        var storepath = objectPop(kw,'storepath'); //deprecated
        var identifier = objectPop(kw,'identifier');
        var caption = objectPop(kw,'caption') || 'caption';
        sourceNode.attr._workspace = true;

        var gnrwdg = sourceNode.gnrwdg;
        if(storepath){
            console.warn('use items attr instead of');
            sourceNode.registerDynAttr('items');
            items = '^'+storepath;
        }
        if(multibuttonstore.len()){
            var storeattr = multibuttonstore.getAttr('#0');
            storeattr.storepath = storeattr.storepath || '#WORKSPACE.store';
            identifier = storeattr._identifier || '_pkey';
            items = '^'+storeattr.storepath;
            sourceNode.registerDynAttr('items')
            storeattr.linkedWidgetNode = sourceNode;
            sourceNode._('SelectionStore','store',storeattr);
        }
        identifier = identifier || 'code';
        var multivalue = objectPop(kw,'multivalue');
        var sticky = objectPop(kw,'sticky') == false ? false:true;
        var mandatory = objectPop(kw,'mandatory',sticky);
        var deleteAction = objectPop(kw,'deleteAction');
        var showAlways = objectPop(kw,'showAlways');
        
        var items_bag = items?sourceNode.getRelativeData(items):new gnr.GnrBag();
        var childItemsPost = new gnr.GnrBag();
        var childItemsPrev = new gnr.GnrBag();
        subTagItems['item'].forEach(function(n){
            var attr = n.attr;
            attr.code = attr.code || n.label;
            if(attr.prev){
                childItemsPrev.setItem(attr.code,null,attr);
            }
            childItemsPost.setItem(attr.code,null,attr);
        });
        gnrwdg.childItemsPrev = childItemsPrev;
        gnrwdg.childItemsPost = childItemsPost;
        gnrwdg.showAlways = showAlways;
        gnrwdg.sticky = sticky;
        gnrwdg.mandatory = mandatory;
        gnrwdg.identifier = identifier;
        gnrwdg.caption = caption;
        gnrwdg.caption_format = objectPop(kw,'caption_format');
        gnrwdg.caption_dtype = objectPop(kw,'caption_dtype');
        if(values){
            items_bag = gnrwdg.itemsFromValues(values);
        }
        items = items || '^#WORKSPACE.items';
        sourceNode.registerDynAttr('items');
        if(deleteAction){
            gnrwdg.deleteAction = funcCreate(deleteAction,'value,caption',gnrwdg.sourceNode);
            gnrwdg.deleteSelectedOnly = objectPop(kw,'deleteSelectedOnly');
        }
        sourceNode.attr.value = value;
        sourceNode.attr.values = values;
        sourceNode.attr.items = items;
        var containerKw = {_class:'multibutton_container'};
        if (sticky){
            var btn_action = function(event){
                var sn = event.target?genro.dom.getBaseSourceNode(event.target):null;
                if(sn){
                    var mcode = sn.getInheritedAttributes()['multibutton_code'];
                    if(mcode){
                        if(event.shiftKey && multivalue){
                            var prevmcode = sourceNode.getRelativeData(value);
                            if(prevmcode){
                                prevmcode = prevmcode.split(',');
                                var j = prevmcode.indexOf(mcode);
                                if(j<0){
                                    prevmcode.push(mcode);
                                }else if(prevmcode.length>1 || !mandatory){
                                    prevmcode.splice(j,1);
                                }
                                mcode = prevmcode.join(',');
                            }
                        }
                        sourceNode.setRelativeData(value,mcode);
                    }
                }
            };
        }else{
            var btn_action = function(_kwargs){
                var event=_kwargs.event

                var sn = event.target?genro.dom.getBaseSourceNode(event.target):null;
                if(sn){
                    var mcode = sn.getInheritedAttributes()['multibutton_code'];
                    if(mcode){
                        this.fireEvent(value,objectUpdate(_kwargs,{action:mcode}))
                    }
                }
            }
        }
        containerKw.action = btn_action;
        containerKw.selfsubscribe_appendItem = function(kw){
            gnrwdg.appendItem(kw);
        }
        var multibutton = sourceNode._('div','multibutton',objectUpdate(containerKw,kw));
        gnrwdg.multibuttonSource = multibutton;

        
        if(items_bag){
            sourceNode.setRelativeData(sourceNode.attr.items,items_bag);
            gnrwdg.makeButtons(items_bag);
        }
        return multibutton;
    },

    gnrwdg_itemsFromValues:function(values){
        var result = new gnr.GnrBag();
        if(!values){
            return result;
        }
        if(this.sourceNode.isPointerPath(values[0])){
            values = this.sourceNode.getAttributeFromDatasource('values')
        }
        if(!values){
            return result;
        }
        var l;
        var attr;
        var that = this;
        values.split(',').forEach(function(n){
            l = n.split(':');
            attr = {};
            attr[that.identifier] = l[0];
            attr[that.caption] = l[1] || l[0];
            result.setItem(l[0],null,attr);
        });
        return result;
    },
    

    gnrwdg_selectByNumber:function(buttonNumber,defaultLast){
        var items = this.getItems();
        if(!items || items.len()==0){
            return;
        }
        if(buttonNumber>items.len()-1){
            buttonNumber = defaultLast?(items.len()-1):0;
        }
        var node = items.getNode('#'+buttonNumber);

        this.sourceNode.setRelativeData(this.sourceNode.attr.value, node.attr[this.identifier])
    },

    gnrwdg_setValue:function(value,kw){
        if (this.sticky){
            var mb = this.multibuttonSource;
            if (value && mb){
                value = value.split(',');
                var identifier = this.identifier;
                var code;
                mb.forEach(function(n){
                    if('multibutton_code' in n.attr){
                        code = n.attr.multibutton_code;
                    }else{
                        console.warn('missing multibutton_code');
                        code = n.attr[identifier] || n.attr['code'] || n.label;
                    }
                    genro.dom.setClass(n,'multibutton_selected',value.indexOf(code)>=0);
                });
            } 
        }
    },

    gnrwdg_setValues:function(values,kw){
        this.sourceNode.setRelativeData(this.sourceNode.attr.items,this.itemsFromValues(values));
    },

    gnrwdg_appendItem:function(kw){
        var selectLast = objectPop(kw,'selectLast');
        var store = this.sourceNode.getRelativeData(this.sourceNode.attr.items);
        var identifier = kw[this.identifier];
        store.setItem(flattenString(identifier),null,kw);
        if(selectLast){
            this.sourceNode.setRelativeData(this.sourceNode.attr.value,identifier);
        }
    },

    gnrwdg_defaultDeleteAction:function(key,value){
        var store = this.sourceNode.getRelativeData(this.sourceNode.attr.items);
        var nodeToDel = store.getNodeByAttr(this.identifier,key);
        store.popNode(nodeToDel.label);
    },

    gnrwdg_setItems:function(items,kw,trigger_reason){
        var sn = this.sourceNode;
        //var currentSelectedNode = genro.getDataNode(sn.absDatapath(sn.attr.value))
        var currentSelected = sn.getRelativeData(sn.attr.value);
        if(currentSelected && !this.getItemNode(currentSelected)){
            sn.setRelativeData(sn.attr.value,null);
        }
        this.makeButtons(this.getItems());
    },

    gnrwdg_getItemNode:function(identifier){
        var items = this.getItems();
        if(!items){
            return;
        }
        return items.getNodeByAttr(this.identifier,identifier);
    },

    gnrwdg_getItems:function(){
        return this.sourceNode.getRelativeData(this.sourceNode.attr.items);
    },

    gnrwdg_makeButtons:function(items){
        items = items || new gnr.GnrBag();
        var sourceNode = this.sourceNode;
        var mb = this.multibuttonSource;
        var child_count = items.len();
        var deleteAction = this.deleteAction;
        var customDelete;
        var gnrwdg = this;
        mb.clear(true);
        if (mb){
            var btn,content_kw,btn_class,code,caption,kw;
            var firstItem = items.getNode('#0');
            var currentSelected = sourceNode.getRelativeData(sourceNode.attr.value);
            //if(!currentSelected && this.mandatory && firstItem){
            //    currentSelected = firstItem.attr[gnrwdg.identifier] || firstItem.label;
            //}
            var that = this;
            this.childItemsPrev.forEach(function(n){
                that.oneButton(n,currentSelected,'code','caption');
            },'static');
            items.forEach(function(n){
                that.oneButton(n,currentSelected);
            },'static');
            this.childItemsPost.forEach(function(n){
                that.oneButton(n,currentSelected,'code','caption');
            },'static');
            if(!currentSelected && this.mandatory && this.multibuttonSource.len()){
                var currentSelectedNode = this.multibuttonSource.getNode('#0');
                if(currentSelectedNode && !currentSelectedNode.attr.action){
                    currentSelectedNode.attr['_class'] +=' multibutton_selected';
                    currentSelected = currentSelectedNode.attr[this.identifier] || currentSelectedNode.attr['code'] || currentSelectedNode.label;
                }
            }
            sourceNode.setRelativeData(sourceNode.attr.value,currentSelected);

        }
    },
    gnrwdg_oneButton:function(n,currentSelected,identifier,caption){
        var mb = this.multibuttonSource;
        var kw = objectUpdate({},n.attr);
        var content_kw = objectExtract(kw,'content_*');
        content_kw._class = objectPop(content_kw,'class');
        var captionKey = caption || this.caption;
        var codeKey = identifier || this.identifier;
        var caption = kw[captionKey];
        var code = kw[codeKey] || n.label;
        var btn_class = code==currentSelected?'multibutton multibutton_selected':'multibutton';
        var customDelete = kw.deleteAction;
        if(typeof(customDelete)=='string'){
            customDelete = funcCreate(kw.deleteAction,'value,caption')
        }
        var deleteAction = customDelete===false?false:(customDelete || this.deleteAction);
        if(kw._is_readonly_row){
            btn_class =btn_class + ' _is_readonly_row';
        }
        else if(deleteAction){
            btn_class = btn_class +' multibutton_closable';
        }
        kw.multibutton_code = code;
        kw._class = (kw._class || '') +' '+btn_class;
        content_kw.innerHTML = _F(caption,this.caption_format,this.caption_dtype);
        content_kw._class = (content_kw._class || '') + ' '+'multibutton_caption';
        var btn = mb._('lightbutton',kw);
        btn._('div',content_kw);
        var gnrwdg = this;
        if(deleteAction){
            btn._('div',{_class:'multibutton_closer framecloserIcon'+(this.deleteSelectedOnly?' deleteSelectedOnly':''),
                connect_onclick:function(e){
                dojo.stopEvent(e);
                if(deleteAction===true){
                    console.log('defaultDeleteAction');
                    gnrwdg.defaultDeleteAction(code,caption);
                }else{
                    deleteAction.call(this.sourceNode,code,caption);
                }
                
            }});
        }
    },
    gnrwdg_isVisible:function(){
        return genro.dom.isVisible(this.sourceNode.getParentNode())
    }
});

dojo.declare("gnr.widgets.StackButtons", gnr.widgets.gnrwdg, {
    contentKwargs: function(sourceNode, attributes) {
        return attributes;
    },
    createContent:function(sourceNode, kw,children) {
        var frameCode = objectPop(kw,'frameCode');
        var stackNode = objectPop(kw,'stack');
        if(!stackNode){
            genro.assert(kw.stackNodeId,'Need the stack node or the stackNodeId')
            stackNode = genro.nodeById(kw.stackNodeId);
        }
        var that = this;
        kw = objectUpdate({connect_onclick:function(e){
            var childSourceNode =  e.target.sourceNode?e.target.sourceNode.getInheritedAttributes()['_childSourceNode']:null;
            var buttonNode = genro.dom.getBaseSourceNode(e.target);
            var buttonAttr = buttonNode.currentAttributes();
            if(buttonAttr.disabled){
                return;
            }
            if(childSourceNode){
                stackNode.widget.selectChild(childSourceNode.widget);
            }
        },_class:'multibutton_container'},kw);
        var tabButtonsNode = sourceNode._('div',kw);
        stackNode._n_children = 0
        if(children && children.len()>0){
            stackNode._n_children = children.len();
        }
        stackNode._stackButtonsNodes = stackNode._stackButtonsNodes || [];
        stackNode._stackButtonsNodes.push(tabButtonsNode.getParentNode());
        dojo.connect(stackNode,'onNodeBuilt',function(widget){
            genro.callAfter(function(){
                that.initButtons(stackNode);
                dojo.connect(widget.gnr,'onShowHideChild',that,'onShowHideChild');
                dojo.connect(widget.gnr,'onAddChild',that,'onAddChild');
                dojo.connect(widget.gnr,'onRemoveChild',that,'onRemoveChild');
                dojo.connect(widget,'setHiddenChild',function(child,value){
                    that.setHiddenChild(this,child,value);
                });
            },1)
        })
        return tabButtonsNode;
    },
    onAddChild:function(widget,child){
        var sn = widget.sourceNode;
        var controllerNodes = sn._stackButtonsNodes;
        
        if((!controllerNodes) || sn._isBuilding){
            return;
        }
        var that = this;
        sn.delayedCall(function(){
            var cn = sn._stackButtonsNodes;
            if(cn){
                dojo.forEach(cn,function(c){
                    that.makeTabButton(c,child.sourceNode,sn);
                });
            }
        },100);
    },
    onRemoveChild:function(widget,child){
        var sn = widget.sourceNode;
        var controllerNodes = sn._stackButtonsNodes;
        
        if((!controllerNodes) || sn._isBuilding){
            return;
        }
        var paneId = this.getPaneId(child.sourceNode);
        setTimeout(function(){
            dojo.forEach(controllerNodes,function(c){
                c._value.popNode(paneId);
            });
        },1)
    },
    setHiddenChild:function(widget,child,value){
        var sn = widget.sourceNode;
        var controllerNodes = sn._stackButtonsNodes;
        
        if((!controllerNodes) || sn._isBuilding){
            return;
        }
        var paneId = this.getPaneId(child.sourceNode);
        dojo.forEach(controllerNodes,function(c){
            genro.dom.setClass(c._value.getNode(paneId),'hidden',value)
        })
    },

    onShowHideChild:function(widget, child, st){
        if(!child){
            return;
        }
        var sn = widget.sourceNode;
        var paneId = this.getPaneId(child.sourceNode);
        var controllerNodes = widget.sourceNode._stackButtonsNodes;
        if((!controllerNodes) || sn._isBuilding){
            return;
        }
        dojo.forEach(controllerNodes,function(c){
            genro.dom.setClass(c._value.getNode(paneId),'multibutton_selected',st)
        })
        
    },
    initButtons:function(stackNode){
        var controllerNodes = stackNode._stackButtonsNodes;
        var sc = stackNode.widget;
        var page;
        var that = this;
        if(!controllerNodes){
            return;
        }
        stackNode._value.forEach(function(n){
            if(n.getWidget()){
                dojo.forEach(controllerNodes,function(c){
                    that.makeTabButton(c,n,stackNode);
                });
            }
        });
    },
    getPaneId:function(childSourceNode){
        var result = childSourceNode.attr.pageName || childSourceNode.attr.nodeId || childSourceNode.getStringId();
        return flattenString(result);
    },
    makeTabButton:function(sourceNode,childSourceNode,stackNode){
        var widget = childSourceNode.getWidget();
        var childSourceNode = widget.sourceNode;
        if(childSourceNode.attr.title){
            var btn_class = widget.selected? 'multibutton multibutton_selected' :'multibutton';
            if(childSourceNode.attr.closable){
                btn_class+=' multibutton_closable'
            }
            var stackbag = stackNode.getValue();
            var childattr = childSourceNode.attr;
            var multibutton_kw = objectExtract(childattr,'stackbutton_*');
            var btn_kw = {_class:btn_class,_childSourceNode:childSourceNode};
            var btn = sourceNode._('div',this.getPaneId(childSourceNode),btn_kw,{_position:stackbag.len()-stackNode._n_children});
            var title = childSourceNode.attr.title;
            var iconTitle = childSourceNode.attr.iconTitle;
            if(title && title[0]=='^'){
                title = '^'+childSourceNode.absDatapath(title);
            }
            if(iconTitle){
                multibutton_kw.innerHTML = '&nbsp;'
                multibutton_kw._class= 'multibutton_caption '+iconTitle
                multibutton_kw.tip = title;
            }else{
                multibutton_kw.innerHTML = title;
                multibutton_kw._class = 'multibutton_caption';
            }
            btn._('div',multibutton_kw);
            if(childSourceNode.attr.closable){
                var stack = stackNode.widget;
                var onClosingCb = childSourceNode.attr.onClosingCb;
                var closeFinalize = function(){
                    genro.callAfter(function(){
                        if(stackbag.len()>1){
                            var idx = stack.getSelectedIndex()-1;
                            idx = idx>=0?idx:0;
                            stack.switchPage(idx);
                        }
                        stackbag.popNode(childSourceNode.label);
                    },1);
                };
                btn._('div',{_class:'multibutton_closer framecloserIcon',connect_onclick:function(evt){
                    dojo.stopEvent(evt);
                    if(onClosingCb){
                        var r = funcApply(onClosingCb,{evt:evt},childSourceNode);
                        if(r===false){
                            return
                        }else if(typeof(r)=='string'){
                            genro.dlg.ask(_T('Closing page')+childSourceNode.getRelativeData(title),r,
                                            {confirm:_T('Close anyway'),cancel:_T('Cancel')},
                                            {confirm:function(){
                                                closeFinalize();
                                            }, cancel:function(){}});
                        }else{
                            closeFinalize();
                        }
                    }else{
                        closeFinalize();
                    }
                }});
            }
        }
    }
});
dojo.declare("gnr.widgets.UserObjectBar", gnr.widgets.gnrwdg, {
    createContent:function(sourceNode,kw){
        var gnrwdg = sourceNode.gnrwdg;
        sourceNode.attr.nodeId = objectPop(kw,'nodeId');
        if(objectPop(kw,'_workspace')!==false){
            sourceNode.attr._workspace = true;
        }
        var userObjectPars = objectExtract(kw,'table,flags,objtype');
        userObjectPars.objtype = userObjectPars.objtype;
        gnrwdg.newcaption  = _T(objectPop(kw,'newcaption') ||  'New '+userObjectPars.objtype);
        gnrwdg.table = userObjectPars.table;
        objectUpdate(userObjectPars,objectExtract(kw,'userobject_*'));
        gnrwdg.userObjectPars = userObjectPars;
        gnrwdg.startUserObjectIdOrCode = kw.userObjectId;
        gnrwdg.dataIndex = objectExtract(kw,'source_');
        gnrwdg.metadataPath = this.sourceNode.absDatapath(kw.metadata) || this.sourceNode.absDatapath('#WORKSPACE.metadata');
        return gnrwdg.buildToolbar(sourceNode);
    },

    gnrwdg_buildToolbar:function(sourceNode){
        this.setLoadMenuData();
        var bar = sourceNode._('slotBar',{toolbar:true,side:'top',slots:'5,loadMenu,2,objTitle,*,favoritebtn,saveBtn,deletebtn,5'});
        var that = this;
        bar._('div','objTitle',{innerHTML:'^.description?=(#v || "New")',
                                datapath:this.metadataPath,font_weight:'bold',
                                font_size:'.9em',color:'#666'});
        bar._('slotButton','favoritebtn',{'label':_T('Default'),
                                                    action:function(){that.setCurrentAsFavorite();},
                                                    iconClass:'highlightable iconbox star'});
        
        bar._('slotButton','loadMenu',{iconClass:'iconbox folder',label:'Load',
            menupath:'#WORKSPACE.loadMenu',action:function(item){
                that.loadObject(item.pkey);
        }});
        bar._('slotButton','saveBtn',{iconClass:'iconbox save',label:'Save',
                                        action:function(){
                                            that.saveObject();
                                        }});
        bar._('slotButton','deletebtn',{'label':_T('Delete'),iconClass:'iconbox trash',
                    action:function(){
                        that.deleteCurrentObject();
                    }});
        return bar;
    },

    gnrwdg_resetMenuData:function(){
        var n = this.sourceNode.getRelativeData('#WORKSPACE').getNode('loadMenu');
        n.getResolver().reset();
    },

    gnrwdg_setLoadMenuData:function(){
        this.sourceNode.setRelativeData('#WORKSPACE.loadMenu',
                                        genro.dev.userObjectMenuData(objectUpdate({},this.userObjectPars),
                                                    [{pkey:'__newobj__',caption:this.newcaption}]));
    },

    gnrwdg_prepareViewerFrame:function(bc,kw){
        //override
        var frame = bc._('FramePane','viewer',{region:'center',frameCode:this.sourceNode.attr.nodeId+'_viewer'});
        this.viewerFrame(frame);
    },

    gnrwdg_setCurrentAsFavorite:function(){
        var metadata = this.sourceNode.getRelativeData(this.metadataPath);
        var pkey = metadata.getItem('pkey');
        genro.setInStorage("local", this.storageKey(), pkey);
        this.checkFavorite();
    },

    gnrwdg_getFavorite:function(){
        return  genro.getFromStorage("local", this.storageKey());
    },

    gnrwdg_checkFavorite:function(){
        var metadata = this.sourceNode.getRelativeData(this.metadataPath) || new gnr.GnrBag();
        var pkey = metadata.getItem('pkey');
        var currfavorite = this.getFavorite();
        genro.dom.setClass(this.sourceNode.getValue().getNode('rootbc'),'highlighted',currfavorite==pkey);
    },

    gnrwdg_storageKey:function(){
        return this.userObjectPars.objtype + genro.getData('gnr.pagename') + '_' + this.sourceNode.attr.nodeId;
    },

    gnrwdg_deleteCurrentObject:function() {
        var metadata = this.sourceNode.getRelativeData(this.metadataPath);
        var pkey = metadata.getItem('pkey');
        var that = this;
        if(pkey){
            genro.serverCall('_table.adm.userobject.deleteUserObject',{pkey:pkey},function(){
                that.loadObject('__newobj__');
                that.resetMenuData();
            });
        }else{
             that.loadObject('__newobj__');
        }
    },

    gnrwdg_saveObject:function() {
        var currentMetadata = this.sourceNode.getRelativeData(this.metadataPath);
        var kw = kw || {};
        kw.dataIndex = {};
        kw.objtype = this.userObjectPars.objtype;
        kw.metadataPath = this.metadataPath;
        kw.table = this.title;
        kw.title = _T('Save '+this.userObjectPars.objtype);
        kw.defaultMetadata = {flags:'grid|'+gridNode.attr.nodeId};
        var onSaved = objectPop(kw,'onSaved');
        var that = this;
        if(!onSaved){
            onSaved =function(result){
                that.resetMenuData();
            };
        }
        genro.dev.userObjectSave(sourceNode,kw,onSaved);
    },

    gnrwdg_loadObject:function(userObjectId,firstLoad){
        this.onLoadingObject(userObjectId,firstLoad);
        if(userObjectId=='__newobj__'){
            this.sourceNode.setRelativeData('#WORKSPACE.metadata',null);
            this.onLoadedObject(null,userObjectId,firstLoad);
        }else{
            var that = this;
            genro.serverCall('_table.adm.userobject.loadUserObject', {userObjectIdOrCode:userObjectId,
                                                                    objtype:this.userObjectPars.objtype,
                                                                    tbl:this.userObjectPars.table,
                                                                    flags:this.userObjectPars.flags}, 
            function(result){
                if (result){
                    that.sourceNode.setRelativeData('#WORKSPACE.metadata',new gnr.GnrBag(result.attr));
                    that.onLoadedObject(result,userObjectId,firstLoad);
                }else{
                    var currfavorite = that.getFavorite();
                    if(currfavorite==userObjectId){
                        genro.setInStorage("local", that.storageKey(), null);
                    }
                }
                that.checkFavorite();
            });
        }
    },

    gnrwdg_onLoadingObject:function(userObjectId,firstLoad){
        //override
    },

    gnrwdg_onLoadedObject:function(result,userObjectId,firstLoad){
        //override
    },

});


dojo.declare("gnr.widgets.UserObjectLayout", gnr.widgets.gnrwdg, {
    //legacy
    objtype:null,
    default_configurator_pars:null,
    newcaption:null,
    createContent:function(sourceNode,kw){
        var gnrwdg = sourceNode.gnrwdg;
        sourceNode.attr.nodeId = objectPop(kw,'nodeId');
        if(objectPop(kw,'_workspace')!==false){
            sourceNode.attr._workspace = true;
        }
        var userObjectPars = objectExtract(kw,'table,flags,objtype');
        userObjectPars.objtype = userObjectPars.objtype || this.objtype;
        gnrwdg.newcaption  = _T(objectPop(kw,'newcaption') || this.newcaption ||  'New '+userObjectPars.objtype);
        gnrwdg.table = userObjectPars.table;
        objectUpdate(userObjectPars,objectExtract(kw,'userobject_*'));
        gnrwdg.userObjectPars = userObjectPars;
        
        var bc = sourceNode._('BorderContainer','rootbc',objectExtract(kw,'top,bottom,left,right,border,margin,height,width,rounded,region,side'));
        kw.userObjectId = gnrwdg.getFavorite() || kw.userObjectId;  
        gnrwdg.startUserObjectIdOrCode = kw.userObjectId;
        kw.configurator = kw.configurator===false?false:(kw.configurator|| this.default_configurator_pars);
        if(kw.configurator){
            gnrwdg.prepareConfiguratorFrame(bc,kw);
        }
        gnrwdg.prepareViewerFrame(bc,kw);
        return bc;
    },

    gnrwdg_resetMenuData:function(){
        var n = this.sourceNode.getRelativeData('#WORKSPACE').getNode('loadMenu');
        n.getResolver().reset();
    },

    gnrwdg_setLoadMenuData:function(){
        this.sourceNode.setRelativeData('#WORKSPACE.loadMenu',
                                        genro.dev.userObjectMenuData(objectUpdate({},this.userObjectPars),
                                                    [{pkey:'__newobj__',caption:this.newcaption}]));
    },

    gnrwdg_prepareViewerFrame:function(bc,kw){
        //override
        var frame = bc._('FramePane','viewer',{region:'center',frameCode:this.sourceNode.attr.nodeId+'_viewer'});
        this.viewerFrame(frame);
    },


    gnrwdg_viewerFrame:function(frame,kw){
        //override
    },

    gnrwdg_configuratorFrame:function(frame,kw){
        //override
    },

    gnrwdg_prepareConfiguratorFrame:function(bc,kw){
        var confkw = objectPop(kw,'configurator');
        confkw = confkw===true?{region:'right',splitter:true,border_left:'1px solid #ccc',width:'320px'}:confkw;  
        var confroot = bc;
        this.setLoadMenuData();
        var frame;
        if(confkw.palette){
            confkw.paletteCode = this.sourceNode.attr.nodeId+'_conf_palette';
            this.conf_paletteCode = confkw.paletteCode;
            frame = bc._('PalettePane','configurator',confkw)._('framePane',{frameCode:this.sourceNode.attr.nodeId+'_conf'});
        }else{
            if(!('drawer' in confkw)){
                confkw.drawer = (kw.userObjectId && kw.userObjectId!='__newobj__')?'close':true;
            } 
            frame = bc._('FramePane','configurator',objectUpdate(confkw,{frameCode:this.sourceNode.attr.nodeId+'_conf'}));
        }
        var bar = frame._('slotBar',{toolbar:true,side:'top',slots:'5,loadMenu,2,objTitle,*,favoritebtn,saveBtn,deletebtn,5'});
        var that = this;
        bar._('div','objTitle',{innerHTML:'^#WORKSPACE.metadata.description?=(#v || "New")',font_weight:'bold',font_size:'.9em',color:'#666'});
        bar._('slotButton','favoritebtn',{'label':_T('Default'),
                                                    action:function(){that.setCurrentAsFavorite();},
                                                    iconClass:'highlightable iconbox star'});
        
        bar._('slotButton','loadMenu',{iconClass:'iconbox folder',label:'Load',
            menupath:'#WORKSPACE.loadMenu',action:function(item){
                that.loadObject(item.pkey);
        }});
        bar._('slotButton','saveBtn',{iconClass:'iconbox save',label:'Save',
                                        action:function(){
                                            that.saveObject();
                                        }});
        bar._('slotButton','deletebtn',{'label':_T('Delete'),iconClass:'iconbox trash',
                    action:function(){
                        that.deleteCurrentObject();
                    }});

        this.configuratorFrame(frame,kw);
    },

    gnrwdg_setCurrentAsFavorite:function(){
        var metadata = this.sourceNode.getRelativeData('#WORKSPACE.metadata');
        var pkey = metadata.getItem('pkey');
        genro.setInStorage("local", this.storageKey(), pkey);
        this.checkFavorite();
    },

    gnrwdg_getFavorite:function(){
        return  genro.getFromStorage("local", this.storageKey());
    },

    gnrwdg_checkFavorite:function(){
        var metadata = this.sourceNode.getRelativeData('#WORKSPACE.metadata') || new gnr.GnrBag();
        var pkey = metadata.getItem('pkey');
        var currfavorite = this.getFavorite();
        genro.dom.setClass(this.sourceNode.getValue().getNode('rootbc'),'highlighted',currfavorite==pkey);
    },

    gnrwdg_storageKey:function(){
        return this.userObjectPars.objtype + genro.getData('gnr.pagename') + '_' + this.sourceNode.attr.nodeId;
    },


    gnrwdg_userObjectData:function(){
        //override
        return new gnr.GnrBag();
    },

    gnrwdg_deleteCurrentObject:function() {
        var metadata = this.sourceNode.getRelativeData('#WORKSPACE.metadata');
        var pkey = metadata.getItem('pkey');
        var that = this;
        if(pkey){
            genro.serverCall('_table.adm.userobject.deleteUserObject',{pkey:pkey},function(){
                that.loadObject('__newobj__');
                that.resetMenuData();
            });
        }else{
             that.loadObject('__newobj__');
        }
    },

    gnrwdg_saveObject:function() {
        var datapath = this.sourceNode.absDatapath('#WORKSPACE.metadata');
        var instanceCode = this.sourceNode.getRelativeData('#WORKSPACE.metadata.code');
        var data = this.userObjectData();
        var that = this;
        saveCb = function(dlg,event,counter,modifiers) {
            var metadata = genro.getData(datapath);
            metadata.setItem('flags',that.userObjectPars.flags);
            genro.serverCall('_table.adm.userobject.saveUserObject',
                            {'objtype':that.userObjectPars.objtype,'metadata':metadata,
                            'data':data,table:that.userObjectPars.table},
                            function(result) {
                                dlg.close_action();
                                metadata.setItem('pkey',result.getValue());
                                that.resetMenuData();
                            });
        };
        genro.dev.userObjectDialog(instanceCode ? 'Save ' + this.userObjectPars.objtype +' '+instanceCode : 'Save '+this.newcaption,datapath,saveCb);
    },

    gnrwdg_loadObject:function(userObjectId,firstLoad){
        this.onLoadingObject(userObjectId,firstLoad);
        if(userObjectId=='__newobj__'){
            this.sourceNode.setRelativeData('#WORKSPACE.metadata',null);
            this.onLoadedObject(null,userObjectId,firstLoad);
        }else{
            var that = this;
            genro.serverCall('_table.adm.userobject.loadUserObject', {userObjectIdOrCode:userObjectId,
                                                                    objtype:this.userObjectPars.objtype,
                                                                    tbl:this.userObjectPars.table,
                                                                    flags:this.userObjectPars.flags}, 
            function(result){
                if (result){
                    that.sourceNode.setRelativeData('#WORKSPACE.metadata',new gnr.GnrBag(result.attr));
                    that.onLoadedObject(result,userObjectId,firstLoad);
                }else{
                    var currfavorite = that.getFavorite();
                    if(currfavorite==userObjectId){
                        genro.setInStorage("local", that.storageKey(), null);
                    }
                }
                that.checkFavorite();
            });
        }
    },

    gnrwdg_onLoadingObject:function(userObjectId,firstLoad){
        //override
    },

    gnrwdg_onLoadedObject:function(result,userObjectId,firstLoad){
        //override
    },
});



dojo.declare("gnr.widgets.SharedObject", gnr.widgets.gnrwdg, {
    createContent:function(sourceNode,kw){
        sourceNode.gnrwdg.sharedKw = objectUpdate({},kw);
        kw.script = "this.getParentNode().gnrwdg.handleSubscriptions(_triggerpars.kw.oldvalue);";
        var dc = sourceNode._('dataController',kw);
        sourceNode.gnrwdg.handleSubscriptions();
        return dc;
    },

    gnrwdg_handleSubscriptions:function(old_shared_id){
        var sharedKw = this.sourceNode.evaluateOnNode(this.sharedKw);
        var shared_id=objectPop(sharedKw,'shared_id');
        var path = objectPop(sharedKw,'shared_path');
        if(old_shared_id){
            genro.som.unregisterSharedObject(old_shared_id);
        }
        if(shared_id && path){
            genro.som.registerSharedObject(this.sourceNode.absDatapath(path),shared_id,sharedKw);
        }
    }
});

dojo.declare("gnr.widgets.ComboArrow", gnr.widgets.gnrwdg, {
    createContent:function(sourceNode,kw,childSourceNode){
        var focusNode;
        var curNode = sourceNode;
        while (!focusNode){
            if(curNode.widget){
                focusNode = curNode.widget.focusNode;
            }
            curNode = curNode.getParentBag().getParentNode()
        }
        genro.dom.addClass(focusNode.parentNode,'comboArrowTextbox')

        var iconClass = objectPop(kw,'iconClass') || 'dijitArrowButtonInner';
        var box= sourceNode._('div',objectUpdate({'_class':'fakeButton',cursor:'pointer', width:'20px',
                                position:'absolute',top:0,bottom:0,right:0,tabindex:-1},kw))
        box._('div','iconNode',{_class:iconClass,position:'absolute',top:0,bottom:0,left:0,right:0})
        return box;
    }
});

dojo.declare("gnr.widgets.PackageSelect", gnr.widgets.gnrwdg, {
    createContent:function(sourceNode,kw,childSourceNode){
        kw.hasDownArrow = true;
        
        kw.onCreating = function(attributes){
            var that = this;
            genro.serverCall('app.dbStructure',{path:''},function(result){
                that._cbstore = result.getNodes().map(function(n){return {_pkey:n.label,pkg:n.label,caption:n.label,name:n.attr.caption};});
            });
        };

        kw.callback = function(cbkw){
            var _id = cbkw._id;
            var _querystring = cbkw._querystring;
            var cbfilter = function(n){return true};
            if(_querystring){
                _querystring = _querystring.slice(0,-1).toLowerCase();
                cbfilter = function(n){return (n.name && n.name.toLowerCase().indexOf(_querystring)>=0) || n.pkg.indexOf(_querystring)>=0;};
            }else if(_id){
                cbfilter = function(n){return n._pkey==_id;}
            }
            return {headers:'pkg:Pkgid,name:Name',data:this.sourceNode._cbstore.filter(cbfilter)}
        };
        
        return sourceNode._('CallbackSelect',kw);
    }
});


dojo.declare("gnr.widgets.TableSelect", gnr.widgets.gnrwdg, {
    createContent:function(sourceNode,kw,childSourceNode){
        kw.hasDownArrow = true;
        kw.pkg = kw.pkg.replace('^','=')
        kw.onCreating = function(attributes){
            var that = this;
            genro.serverCall('app.getTablesTree',{},function(result){
                that._cbstore = result;
            });
        };
        kw.callback = function(cbkw){
            var currentPkg = this.sourceNode.getAttributeFromDatasource('pkg');
            var tblmapcb = function(n){
                var caption = currentPkg?n.label:n.attr.tableid;
                return {_pkey:n.attr.tableid,tbl:n.attr.tableid,pkg:n.attr.tableid.split('.')[1],name:caption,caption:caption,pkeyField:n.attr.tableid};
            };
            var data;
            if (currentPkg){
                data = this.sourceNode._cbstore.getItem(currentPkg).getNodes();
            }else{
                data = [];
                this.sourceNode._cbstore.values().forEach(function(pkgcontent){
                    data = data.concat(pkgcontent.getNodes());
                });
            }
            data = data.map(tblmapcb);
            var _id = cbkw._id;
            var _querystring = cbkw._querystring;
            var cbfilter = function(n){return true};
            if(_querystring){
                _querystring = _querystring.slice(0,-1).toLowerCase();
                cbfilter = function(n){return n.name.toLowerCase().indexOf(_querystring)>=0 || n.tbl.indexOf(_querystring)>=0;};
            }else if(_id){
                cbfilter = function(n){return n._pkey==_id;}
            }
            return {headers:'tbl:Table,name:Name,pkeyField:Pkey',data:data.filter(cbfilter)}
        };
        return sourceNode._('CallbackSelect',kw);
    }
});

dojo.declare("gnr.widgets.ComboMenu", gnr.widgets.gnrwdg, {
    createContent:function(sourceNode,kw,childSourceNode){
        kw['modifiers'] = kw['modifiers'] || '*';
        kw['attachTo'] = sourceNode.getParentBag().getParentNode();
        return sourceNode._('comboArrow')._('menu',kw);
    }
});

dojo.declare("gnr.widgets.MultiLineTextbox", gnr.widgets.gnrwdg, {
    createContent:function(sourceNode,kw,childSourceNode){
        var tb = sourceNode._('textbox',kw);
        var tbNode = tb.getParentNode();
        var valuepath = tbNode.absDatapath(kw.value);
        tb._('comboArrow',{connect_onclick:function(){
            var curval = tbNode.widget.getValue();
            var dflt = curval?curval.replace(/\,/g,'\n'):null
            genro.dlg.prompt(_T('Multiline value'),{
                widget:'simpleTextArea',wdg_height:'200px',wdg_margin_right:'10px',
                action:function(value){
                    tbNode.setRelativeData(valuepath,value.replace(/\n/g,','));
                },dflt:dflt,onEnter:null});
        }});
        return tb;
    }
});



dojo.declare("gnr.widgets.CheckBoxText", gnr.widgets.gnrwdg, {
    checker : 'checkbox',
    contentKwargs: function(sourceNode, attributes) {
        return attributes;
    },

    createContent:function(sourceNode, kw,children) { 
        var value = objectPop(kw,'value');
        sourceNode.attr.value = value;
        var originalKwargs = objectUpdate({},kw);
        kw = sourceNode.evaluateOnNode(kw);
        var popup = objectPop(kw,'popup');
        var values = objectPop(kw,'values');
        var codeSeparator = objectPop(kw,'codeSeparator');
        var tb;
        var gnrwdg = sourceNode.gnrwdg;
        var has_code;
        gnrwdg.identifier = objectPop(kw,'identifier')
        gnrwdg.labelAttribute = objectPop(kw,'labelAttribute')
        gnrwdg._valuelabel = kw._valuelabel;
        gnrwdg.remoteValuesRpc = objectPop(kw,'remoteValues');
        gnrwdg.valuesCb = objectPop(kw,'valuesCb');
        gnrwdg.tree_extrakw = objectExtract(kw,'tree_*');
        var onOpening;
        if(codeSeparator!==false){
            codeSeparator =  codeSeparator || ':'
        }
        if(values instanceof gnr.GnrBag){
            has_code = true;
        }else{
            has_code = (codeSeparator && values)?values.indexOf(codeSeparator)>=0:false;
        }
        if(!values){
            var table = objectPop(originalKwargs,'table');
            if(table || gnrwdg.remoteValuesRpc){
                var hierarchical = objectPop(kw,'hierarchical');
                var condition_kw = objectExtract(originalKwargs,'condition_*',null,hierarchical);
                var condition = objectPop(originalKwargs,'condition');
                var dbstore = objectPop(originalKwargs,'dbstore');
                var query_kw = {};
                objectUpdate(query_kw,condition_kw)
                query_kw.table = table;
                query_kw.order_by=objectPop(originalKwargs,'order_by')||condition_kw.order_by;
                if(hierarchical){
                    popup = true;
                    gnrwdg.hierarchical = hierarchical;
                    gnrwdg.treestorepath = kw.treestorepath || 'gnr.workspace._hierarchicalStores.'+(kw.nodeId || table.replace('.','_'));
                    gnrwdg.checkedpath = gnrwdg.treestorepath+'_checkedpaths';
                    query_kw.dbstore = dbstore;
                    query_kw.related_kwargs = objectExtract(originalKwargs,'related_*');
                    query_kw.condition = condition;
                    query_kw.resolved = objectPop(kw,'resolved');
                    query_kw.parent_id =  objectPop(originalKwargs,'parent_id');
                    query_kw.root_id = objectPop(originalKwargs,'root_id');
                    query_kw.caption_field = originalKwargs.labelAttribute;
                    query_kw.alt_pkey_field = objectPop(originalKwargs,'alt_pkey_field');
                    gnrwdg.omitRoot = objectPop(kw,'omitRoot',true);
                }else{
                    query_kw.caption_field = originalKwargs.labelAttribute;
                    query_kw.where = condition;
                    query_kw._storename = dbstore;
                    query_kw.alt_pkey_field = objectPop(originalKwargs,'alt_pkey_field');
                    kw.cols = kw.cols || 1;
                }
                for(var k in query_kw){
                    sourceNode.attr['query_'+k] = query_kw[k];
                }
                gnrwdg.query_kw = query_kw;
                values = sourceNode.gnrwdg.getRemoteValuesFromQuery();
                has_code = true;
            }else if(gnrwdg.valuesCb){
                popup = true;
                has_code = true;
                onOpening = function(){
                    var v = funcApply(gnrwdg.valuesCb,null,sourceNode);
                    gnrwdg.has_code = (codeSeparator && v)?v.indexOf(codeSeparator)>=0:false;
                    gnrwdg.setValues(v);
                }
            }
        }
        var rootNode = sourceNode;
        var table_kw = objectExtract(kw,'table_*');
        if(popup){
            var textBoxId = 'placingTextbox_'+genro.getCounter();
            var tbkw = {'value':has_code?value+'?_displayedValue':value,position:'relative',readOnly:true,nodeId:textBoxId};
            objectExtract(originalKwargs,'table,values,cols,identifier,labelAttribute,popup') //belongs to cbtext
            objectUpdate(tbkw,originalKwargs);
            tb = sourceNode._('textbox',tbkw);
            gnrwdg.textboxNode = tb.getParentNode(); 
            rootNode = tb._('comboArrow')._('tooltipPane',{placingId:textBoxId,onOpening:onOpening})._('div',{padding:'5px',overflow:'auto',max_height:'300px',min_width:'200px'});
        }else{
            table_kw['tooltip']=objectPop(kw,'tooltip');
            console.log('table_kw',table_kw);
            objectExtract(originalKwargs,'table,values,cols,identifier,labelAttribute,popup') //belongs to cbtext
            objectUpdate(table_kw,originalKwargs);
        }
        gnrwdg.rootNode = rootNode;
        if(!gnrwdg.hierarchical){
            var tbl = rootNode._('table',table_kw)._('tbody')
            var tblNode = tbl.getParentNode();
            gnrwdg.captionDict = {};
            gnrwdg.valuesDict = {};
            gnrwdg.tblNode = tblNode;
            gnrwdg.has_code = has_code;
            gnrwdg.codeSeparator = codeSeparator;
            gnrwdg.kw = objectUpdate({},kw);
            tblNode.attr.action = function(attr,cbNode,e){
                if(e.shiftKey && attr.tag.toLowerCase()=='checkbox'){
                    tblNode._value.walk(function(n){
                        if(n.attr.tag=='checkbox'){
                            n.widget.setAttribute('checked',cbNode.widget.checked);
                        }
                    });
                }
                sourceNode.gnrwdg.onCheck();
            };
        }
        gnrwdg.setValues(values);
        return popup?tb:tbl;
    },
    
    gnrwdg_setValues:function(values,kw){
        if(this.values==values){
            return;
        }
        var gnrwdg = this;
        if(this.hierarchical){
            if(this.omitRoot){
                values = values.getItem('root');
            }
            this.sourceNode.setRelativeData(this.treestorepath,values);
            if(!this.treeNode){
                this.createTreeCheckbox();
            }
            var currval = this.sourceNode.getRelativeData(this.sourceNode.attr.value);
            var cb = function(){
                gnrwdg.setHierarchicalCheckedPaths(currval);
            };
        }
        else{
            if(values instanceof gnr.GnrBag){
                var l = [];
                var identifier = this.identifier;
                var labelAttribute = this.labelAttribute;
                values.forEach(function(n){
                    var k = n.label;
                    var caption = n.label;
                    if(identifier){
                        k = n._value? n._value.getItem(identifier):n.attr[identifier];
                    }
                    if(labelAttribute){
                        caption = n._value? n._value.getItem(labelAttribute):n.attr[labelAttribute];
                    }
                    l.push(k+':'+caption);
                },'static');
                values = l.join(',');
            }
            this.values = values;
            this.createCheckers();
            cb = function(){
                gnrwdg.alignCheckedValues();
                gnrwdg.onCheck();
            }
        }
        if(!this.sourceNode._isBuilding){
            cb();
        }else{
            this.sourceNode.watch('buildingNode',function(){
                return !gnrwdg.sourceNode._isBuilding;
            },function(){
                cb();
            },10);
        }
    },

    gnrwdg_createTreeCheckbox:function(){
        var valuepath = this.sourceNode.attr.value.replace('^','');
        var treekw = {storepath:this.treestorepath,hideValues:true,identifier:'treeIdentifier',
                        labelAttribute:'caption',
                        selectedLabelClass:'',_class:'pickerCheckboxTree',
                        checked_pkey:valuepath,
                        checkedPaths:this.checkedpath,
                        checked_caption:valuepath+'?_displayedValue',
                        onChecked:true};
        objectUpdate(treekw,this.tree_extrakw);
        var tree = this.rootNode._('tree',treekw);
        this.treeNode = tree.getParentNode();
    },

    gnrwdg_catch_condition:function(value,kw,trigger_reason){
        this.setValues(this.getRemoteValuesFromQuery());
    },

    gnrwdg_cbgroupReason:function(){
        return 'cbgroup_'+this.sourceNode._id;
    },

    gnrwdg_setHierarchicalCheckedPaths:function(value){
        this._notrigger = true;
        this.sourceNode.setRelativeData(this.checkedpath,null,null,null,this.cbgroupReason());
        if(value){
            var pathsFromPkeys = genro.serverCall('_table.'+this.query_kw.table+'.getHierarchicalPathsFromPkeys',{pkeys:value,related_kwargs:this.query_kw.related_kwargs,
                                                                                                                      dbstore:this.query_kw.dbstore,
                                                                                                                      parent_id:this.query_kw.parent_id,
                                                                                                                      alt_pkey_field:this.query_kw.alt_pkey_field,
                                                                                                                      _sourceNode:this.sourceNode});
                
            
            this.sourceNode.setRelativeData(this.checkedpath,pathsFromPkeys,null,null,this.cbgroupReason());
        }
        this._notrigger = false;
    },

    gnrwdg_setValue:function(value,kw,trigger_reason){
        if(kw.reason==this.cbgroupReason() || this._notrigger){
            return;
        }
        if(this.hierarchical){
            var inEditingGrid = this.sourceNode.grid? this.sourceNode.grid.gnrediting:false;
            if(kw.reason && kw.reason.sourceNode == this.treeNode){
                return;
            }
            if(!inEditingGrid){
                this.setHierarchicalCheckedPaths(value);
            }
            return;
        }
        this.alignCheckedValues();
    },

    gnrwdg_isValidValue:function(value){
        if(!value){
            return true;
        }
        var valuesDict = this.valuesDict;
        return value.split(this.separator).every(function(c){return (c in valuesDict)});
    },

    gnrwdg_getLabelsFromValue:function(value){
        if(!value){
            return
        }
        var valuesDict = this.valuesDict;
        return value.split(this.separator).map(function(c){return valuesDict[c]}).join(this.separator)
    },

    gnrwdg_getValue:function(){
        return this.sourceNode.getAttributeFromDatasource('value');
    },

    gnrwdg_getDisplayedValue:function(){
        if(this.hierarchical){
            return this.sourceNode.getRelativeData(this.sourceNode.attr.value+'?_displayedValue');
        }else{
            return this.has_code?this.sourceNode.getRelativeData(this.sourceNode.attr.value+'?_displayedValue'):this.sourceNode.getAttributeFromDatasource('value');
        }
    },

    gnrwdg_getRemoteValuesFromQuery:function(){
        if(this.hierarchical){
            return genro.serverCall('_table.'+this.query_kw.table+'.getHierarchicalData',objectUpdate({_sourceNode:this.sourceNode},this.query_kw))
        }else{
            var rpc = this.remoteValuesRpc || 'app.getValuesString';
            return genro.serverCall(rpc,objectUpdate({_sourceNode:this.sourceNode},this.query_kw));
        }
        
    },

    gnrwdg_alignCheckedValues:function(){
        var sourceNode = this.sourceNode;
        var textvalue =  sourceNode.getAttributeFromDatasource('value') || '';
        if(!this.isValidValue(textvalue)){
            return;
        }
        var splitter = this.separator;
        var checkcodes = textvalue && this.has_code;  
        if(checkcodes){
            splitter = ',';
        }
        var values = splitStrip(textvalue,splitter);
        var v;
        var checker = this.gnr.checker;
        var compareCb = function(node,value){
            if(checkcodes){
                return node.attr._code == value;
            }
            return node.attr.label.toLowerCase() == value.toLowerCase()
        };
        sourceNode._value.walk(function(n){
            if(n.attr.tag==checker){
                n.widget.setAttribute('checked',dojo.some(values,function(v){return compareCb(n,v)}));
            }
        });
        if(this.has_code){
            this.sourceNode.setRelativeData(this.sourceNode.attr.value+'?_displayedValue',this.getLabelsFromValue(textvalue),null,null,this.cbgroupReason())
        }
    },

    gnrwdg_createCheckers:function(){
        var values = this.values;
        var tblNode = this.tblNode;
        var kw = this.kw;
        var has_code = this.has_code;
        var codeSeparator = this.codeSeparator;
        kw = objectUpdate({},kw);
        tblNode._value.clear(true);
        if(!values){
            return;
        }
        this.separator =  kw.separator || ',';
        var splitter = values.indexOf('\n')>=0? '\n':',';
        var valuelist = splitStrip(values,splitter);
        var cols = objectPop(kw,'cols');

        if(valuelist[0][0]=='/'){
            cols = valuelist.shift();
            cols = parseInt(cols.slice(1)) || 1;
        }
        var curr_row = tblNode._('tr',row_kw);
        var cell,cbpars,label,_code;
        var i = 1;
        var colspan;
        var cell_kw = objectExtract(kw,'cell_*');
        var row_kw = objectExtract(kw,'row_*');
        var label_kw = objectExtract(kw,'label_*',null,true);
        var wdgtag = this.gnr.checker;
        var ghrwdg = this;
        ghrwdg.captionDict = {};
        ghrwdg.valuesDict = {};
        dojo.forEach(valuelist,function(v){
            if(v=='/'){
                curr_row =  tblNode._('tr',row_kw);
                i = 1;
                return;
            }
            if(cols && i>cols){
                i = 1;
                curr_row =  tblNode._('tr',row_kw);
            }
            label = v;
            if(has_code){
                v = v.split(codeSeparator);
                _code = v[0];
                label = v[1];
            }  
            colspan = 1;
            if(label.indexOf('\\')>=0){
                label = label.split('\\');
                colspan = parseInt(label[1]);
                label = label[0];
            }
            var z = objectUpdate(cell_kw,{colspan:colspan});
            cell = curr_row._('td',z);  
            cbpars = {label:label,_code:_code};
            var key = _code || label;
            var value = label || _code;
            ghrwdg.captionDict[value] = key;
            ghrwdg.valuesDict[key] = value;
            if(kw.group){
                cbpars.group = kw.group;
            }
            cell._(wdgtag,objectUpdate(cbpars,label_kw));
            i= i + colspan;
        })
    },

    gnrwdg_onCheck:function(){
        var sourceNode = this.sourceNode;
        var separator = this.separator;
        var has_code = this.has_code;
        var i = 0;
        var labels = [];
        var codes = [];
        var rows = sourceNode.getValue().getItem('#0');
        var sourceNodes = dojo.query('.dijitCheckBoxInput',this.tblNode.domNode).map(function(n){
            return dijit.getEnclosingWidget(n).sourceNode
        });
        dojo.forEach(sourceNodes,function(cbNode){
            if(cbNode.widget.checked){
                if(has_code){
                    codes.push(cbNode.attr._code);
                }
                labels.push(cbNode.attr.label)
            }
        });
        //sourceNode.setRelativeData(sourceNode.attr.value,null,null,null,'cbgroup');
        var fkw = {};
        if(this._valuelabel){
            fkw._valuelabel = this._valuelabel;
        }
        if(has_code){
            fkw._displayedValue = labels.length?labels.join(separator):null;
            sourceNode.setRelativeData(sourceNode.attr.value,codes.length>0?codes.join(','):null,fkw,null,this.cbgroupReason(),null,{_updattr:true});
        }else{
            sourceNode.setRelativeData(sourceNode.attr.value,labels.length>0?labels.join(separator):null,fkw,null,this.cbgroupReason(),null,{_updattr:true});
        }
    },

    cell_onCreating:function(gridEditor,colname,colattr) {
        colattr['popup'] = true;
        colattr['onCreated'] = 'this.widget.focusNode.focus()'
    },

    cell_onDestroying:function(sourceNode,gridEditor,editingInfo){
        var newAttr = {};
        if (sourceNode._saved_attributes.field_getter!=sourceNode._saved_attributes.field){
            newAttr[sourceNode._saved_attributes.field_getter] = sourceNode.gnrwdg.getDisplayedValue();
        }
        sourceNode.gnrwdg._notrigger = true;
        gridEditor.grid.collectionStore().updateRow(editingInfo.row,newAttr);
        sourceNode.gnrwdg._notrigger = false;
    }
        
});

dojo.declare("gnr.widgets.RadioButtonText", gnr.widgets.CheckBoxText, {
    checker:'radiobutton',
    contentKwargs:function(sourceNode,attributes){
        attributes.group = attributes.group || genro.getCounter();
        return attributes;
    }
});



dojo.declare("gnr.widgets.FieldsTree", gnr.widgets.gnrwdg, {
    contentKwargs: function(sourceNode, attributes) {
        return attributes;
    },
    createContent:function(sourceNode, kw,children) {
        var table = objectPop(kw,'table');
        var trash = objectPop(kw,'trash');
        var box_kw = objectExtract(kw,'box_*');
        var box = sourceNode._('div',objectUpdate({_class:'fieldsTreeBox',_lazyBuild:true},box_kw));
        var explorerPath = objectPop(kw,'explorerPath');
        if(explorerPath){
            kw.explorerPath = sourceNode.absDatapath(explorerPath);
        }
        if (trash){
            var trashKw = {_class:'treeTrash'};
            trashKw.dropTarget=true;
            trashKw.dropTypes='trashable';
            trashKw.onDrop_trashable=function(dropInfo,data){
                var sourceNode=genro.src.nodeBySourceNodeId(dropInfo.dragSourceInfo._id);
                if(sourceNode&&sourceNode.attr.onTrashed){
                    funcCreate(sourceNode.attr.onTrashed,'dropInfo,data',sourceNode)(dropInfo,data);
                }
            };
            sourceNode._('div',trashKw);
        }
        genro.dev.fieldsTree(box,table,kw);
        return box;
    }
})

dojo.declare("gnr.widgets.SlotBar", gnr.widgets.gnrwdg, {
    contentKwargs: function(sourceNode, attributes) {
        var frameNode = sourceNode.getParentNode().getParentNode();
        var side=sourceNode.getParentNode().attr.region;
        var framePars = frameNode.attr;
        var sidePars = objectExtract(framePars,'side_*',true);
        var default_orientation = side?((side=='top')||(side=='bottom'))?'horizontal':'vertical':'horizontal';
        var orientation = attributes.orientation || default_orientation;

        attributes.orientation=orientation;
        var buildKw={};
        dojo.forEach(['table','row','cell','lbl'],function(k){
            buildKw[k] = objectExtract(attributes,k+'_*');
            buildKw[k]['_class'] = (buildKw[k]['_class'] || '') + ' slotbar_'+k;
        });
        
        if(orientation=='horizontal'){
            if('height' in attributes){
                buildKw.cell['height']= objectPop(attributes,'height');
            }
        }else{
            if('width' in attributes){
                buildKw.cell['width'] = objectPop(attributes,'width');
            }
        }
        attributes['_class'] = (attributes['_class'] || '')+' slotbar  slotbar_'+orientation+' slotbar_'+side;
        var toolbar = objectPop(attributes,'toolbar');
        if(toolbar===true){
            toolbar = 'top';
        }
        side = side || toolbar;
        if(side){
            attributes['side'] = side;
            attributes['slotbarCode'] = attributes['slotbarCode'] || attributes['frameCode'] +'_'+ side; 
            if(toolbar){
                attributes['_class'] += ' slotbar_toolbar slotbar_toolbar_standard slotbar_toolbar_side_'+side;
                attributes['gradient_from'] = attributes['gradient_from'] || sidePars['gradient_from'];// || genro.dom.themeAttribute('toolbar','gradient_from','silver');
                attributes['gradient_to'] = attributes['gradient_to'] || sidePars['gradient_to'];// || genro.dom.themeAttribute('toolbar','gradient_to','whitesmoke');
                var css3Kw = {'left':[0,'right'],'top':[-90,'bottom'],
                            'right':[180,'left'],'bottom':[90,'top']};
                
                if(attributes.gradient_from || attributes.gradient_to){
                    attributes['border_'+css3Kw[side][1]] = attributes['border_'+css3Kw[side][1]] || '1px solid '+ attributes['gradient_from'] || genro.dom.themeAttribute('toolbar','gradient_from','silver');
                    attributes['gradient_deg'] = css3Kw[side][0];
                }
            }
        }
        buildKw.lbl['_class'] = buildKw.lbl['_class'] || 'slotbar_lbl';
        buildKw.lbl_cell = objectExtract(buildKw.lbl,'cell_*');
        attributes['buildKw'] = buildKw;
        return attributes;
    },
    
    
    createContent:function(sourceNode, kw,children) {
        if(kw.closable){
            var pane = sourceNode.getParentNode();
            var bc = pane.widget.parentBorderContainer;
            bc.gnr.addClosableHandle(bc,pane,kw)
        }
        var slots = objectPop(kw,'slots');
        var orientation = objectPop(kw,'orientation');
        var result = this['createContent_'+orientation](sourceNode,kw,kw.slotbarCode,slots,children);
        dojo.forEach(children._nodes,function(n){if(n.attr.tag=='slot'){children.popNode(n.label);}});
        return result;
    },
    
    
    createContent_horizontal:function(sourceNode,kw,slotbarCode,slots,children){
        var buildKw = objectPop(kw,'buildKw');
        var lblPos = objectPop(buildKw.lbl,'position') || 'N';
        var table = sourceNode._('div',kw)._('table',buildKw.table)._('tbody');
        var rlabel;
        if(lblPos=='T'){
            rlabel=  table._('tr');
        }
        var r = table._('tr',buildKw.row);
        if(lblPos=='B'){
            rlabel=  table._('tr');
        }
        var attr,cell,slotNode,slotValue,slotKw,slotValue;
        var children = children || new gnr.GnrBag();
        var that = this;
        var attr,kwLbl,lbl,labelCell,k;
        var slotArray = splitStrip(slots);
        var counterSpacer = dojo.filter(slotArray,function(s){return s=='*';}).length;
        var spacerWidth = counterSpacer? 100/counterSpacer:100;
        var cellKwLbl = buildKw.lbl_cell;
        dojo.forEach(slotArray,function(slot){
            if(rlabel){
                labelCell = rlabel._('td',cellKwLbl);
            }else if(lblPos=='L'){
                cellKwLbl['width'] = cellKwLbl['width'] || '1px';
                labelCell = r._('td',cellKwLbl);
            }
            if(slot=='*'){
                r._('td',{'_class':'slotbar_elastic_spacer',width:spacerWidth+'%'});
                return;
            };
            if(slot==parseInt(slot)){
                r._('td')._('div',{width:slot+'px'});
                return;
            };
            if(slot=='|'){
                r._('td')._('div',{_class:'slotbar_spacer'});
                return;
            };

            cell = r._('td',objectUpdate({_slotname:slot},buildKw.cell));
            if(lblPos=='R'){
                cellKwLbl['width'] = cellKwLbl['width'] || '1px';
                labelCell = r._('td',cellKwLbl); 
            };
            slotNode = children.popNode(slot);
            if (!that['slot_'+slot] && slotNode){
                if(slotNode.attr.tag=='slot'){
                    slotValue = slotNode.getValue();
                }else{
                    slotValue = new gnr.GnrBag({'slot':slotNode});
                }
                if(slotValue instanceof gnr.GnrBag){
                    k=0;
                    slotValue.forEach(function(n){
                        attr = n.attr;
                        kwLbl = objectExtract(attr,'lbl_*');
                        lbl = objectPop(attr,'lbl');
                        cell.setItem(n.label,n._value,n.attr);
                        if((k==0)&&labelCell){
                            kwLbl = objectUpdate(objectUpdate({},buildKw.lbl),kwLbl);
                            labelCell._('div',objectUpdate({'innerHTML':lbl,'text_align':'center'},kwLbl));
                        }
                        k++;
                    });
                }
            }
            slotKw = objectExtract(kw,slot+'_*');
            if(slotKw.width){
                cell.getParentNode().attr['width'] = slotKw.width;
                slotKw.width = '100%';
            }
            if(slotKw.text_align){
                cell.getParentNode().attr['text_align'] = slotKw.text_align;
            }
            if(cell.len()==0){
                if(that['slot_'+slot]){
                    slotValue = objectPop(kw,slot);
                    lbl = objectPop(slotKw,'lbl');
                    kwLbl = objectExtract(slotKw,'lbl_*');
                    kwLbl = objectUpdate(objectUpdate({},buildKw.lbl),kwLbl);
                    that['slot_'+slot](cell,slotValue,slotKw,kw.frameCode);
                    if(labelCell){
                        labelCell._('div',objectUpdate({'innerHTML':lbl,'text_align':'center'},kwLbl));
                    }
                }else{
                    var textSlot = kw[slot];
                    if(textSlot){
                        cell.setItem('div_0',null,objectUpdate({innerHTML:textSlot,tag:'div'},objectExtract(kw,slot+'_*')));
                    }
                }
            }       
        });
        
        return r;
    },
    createContent_vertical:function(sourceNode,kw,slotbarCode,slots,children){
        var buildKw = objectPop(kw,'buildKw');
        var lblPos = objectPop(buildKw.lbl,'position') || 'N';
        var table = sourceNode._('div',kw)._('table',buildKw.table)._('tbody');

        var attr,row,cell,slotNode,slotValue,slotKw,slotValue;
        var children = children || new gnr.GnrBag();
        var that = this;
        var attr,kwLbl,lbl,labelCell,k;
        var slotArray = splitStrip(slots);
        var cellKwLbl = buildKw.lbl_cell;
        dojo.forEach(slotArray,function(slot){
            /*if(rlabel){
                labelCell = rlabel._('td',cellKwLbl);
            }else if(lblPos=='L'){
                cellKwLbl['width'] = cellKwLbl['width'] || '1px'
                labelCell = r._('td',cellKwLbl)
            }*/
            if(slot=='*'){
                table._('tr');
                return;
            }
            if(slot=='|'){
                table._('tr',{'height':'1px'})._('td')._('div',{_class:'slotbar_spacer'});
                return;
            }
            if(slot==parseInt(slot)){
                table._('tr',{height:slot+'px'});
                return;
            }
            
            row = table._('tr',buildKw.row)
            cell = row._('td',objectUpdate({_slotname:slot,position:'relative'},buildKw.cell));
            /*if(lblPos=='R'){
                cellKwLbl['width'] = cellKwLbl['width'] || '1px';
                labelCell = r._('td',cellKwLbl)
            }*/
            slotNode = children.popNode(slot);
            if (slotNode){
                slotValue = slotNode.getValue();
                if(slotValue instanceof gnr.GnrBag){
                    k=0;
                    slotValue.forEach(function(n){
                        attr = n.attr;
                        kwLbl = objectExtract(attr,'lbl_*');
                        lbl = objectPop(attr,'lbl');
                        cell.setItem(n.label,n._value,n.attr);
                        /*if((k==0)&&labelCell){
                            kwLbl = objectUpdate(objectUpdate({},buildKw.lbl),kwLbl);
                            labelCell._('div',objectUpdate({'innerHTML':lbl,'text_align':'center'},kwLbl));
                        }*/
                        k++;
                    });
                }
                slotKw = objectUpdate({},slotNode.attr);
            }else{
                slotKw = {};
            }
            objectExtract(slotKw,'tag,_childname')
            slotKw = objectUpdate(slotKw,objectExtract(kw,slot+'_*'));
            if(slotKw.height){
                row.getParentNode().attr['height'] = slotKw.height;
                slotKw.height = '100%';
            }
            if(cell.len()==0 && (that['slot_'+slot])){
                slotValue = objectPop(kw,slot);
                lbl = objectPop(slotKw,'lbl');
                kwLbl = objectExtract(slotKw,'lbl_*');
                kwLbl = objectUpdate(objectUpdate({},buildKw.lbl),kwLbl);
                that['slot_'+slot](cell,slotValue,slotKw,kw.frameCode);
                if(labelCell){
                    labelCell._('div',objectUpdate({'innerHTML':lbl,'text_align':'center'},kwLbl));
                }
            }            
        });
        
        return table;
    },
    
    slot_searchOn:function(pane,slotValue,slotKw,frameCode){
        var div = pane._('div'); //{'width':slotKw.width || '15em'}
        var searchId = objectPop(slotKw,'nodeId') || frameCode+'_searchbox';
        var searchCode = objectPop(slotKw,'searchCode');
        if(searchCode){
            searchId = searchCode+'_searchbox';
        }
        div._('SearchBox', {searchOn:slotValue,nodeId:searchId,datapath:'.searchbox',parentForm:false,
                            'width':objectPop(slotKw,'width'),search_kw:slotKw});
    },
    slot_stackButtons:function(pane,slotValue,slotKw,frameCode){
        var scNode = objectPop(slotKw,'stackNode');
        if(scNode){
           scNode = pane.getParentNode().currentFromDatasource(scNode);
        }
        if (!scNode){
            var stackNodeId = objectPop(slotKw,'stackNodeId');
            scNode = stackNodeId?genro.nodeById(stackNodeId):genro.getFrameNode(frameCode,'center');
        }
        pane._('StackButtons',objectUpdate({stack:scNode},slotKw));
    },
    slot_parentStackButtons:function(pane,slotValue,slotKw,frameCode){
        slotKw['height'] = slotKw['height'] || '20px'
        pane._('StackButtons',objectUpdate(objectUpdate({stack:pane.getParentNode().attributeOwnerNode('tag','StackContainer')},slotKw)));
    },
    
    slot_fieldsTree:function(pane,slotValue,slotKw,frameCode){
        var table = objectPop(slotKw,'table');
        table = pane.getParentNode().currentFromDatasource(table);
        var checkPermissions = objectPop(slotKw,'checkPermissions');

        var dragCode = objectPop(slotKw,'dragCode');
        var treeKw = objectExtract(slotKw,'tree_*') || {};
        treeKw.dragCode = dragCode;
        slotKw.text_align = 'left';
        //slotKw.position = 'relative';
        var currRecordPath = objectPop(slotKw,'currRecordPath');
        var explorerPath = objectPop(slotKw,'explorerPath');

        var slot = pane._('div',slotKw);
        slot._('FieldsTree',objectUpdate({table:table,trash:true,currRecordPath:currRecordPath,explorerPath:explorerPath,checkPermissions:checkPermissions},treeKw));
    },
    
    slot_count:function(pane,slotValue,slotKw,frameCode){
        var row = pane._('table',{datapath:'.count',nodeId:frameCode+'_countbox', _class:'countBox'})._('tbody')._('tr');
        row._('td')._('div',{innerHTML:'^.shown',_class:'countBoxPartial'});
        row._('td')._('div',{innerHTML:'^.total',_class:'countBoxTotal'});
    },
    
    slot_messageBox:function(pane,slotValue,slotKw,frameCode){        
        var mbKw = objectUpdate({duration:1000,delay:2000},slotKw);
        var subscriber = objectPop(mbKw,'subscribeTo');
        var default_delay = objectPop(mbKw,'delay');
        var default_duration= objectPop(mbKw,'duration');

        mbKw['subscribe_'+subscriber] = function(){
             var kwargs = arguments[0];
             var domNode = this.domNode;
             var sound = objectPop(kwargs,'sound');
             var duration = objectPop(kwargs,'duration') || default_duration;
             var delay = objectPop(kwargs,'delay') || default_delay;
             if(sound){
                 genro.playSound(sound);
             }
             var message = objectPop(kwargs,'message');
             var msgnode = document.createElement('span');
             msgnode.innerHTML = message;
             genro.dom.style(msgnode,kwargs);
             domNode.appendChild(msgnode);
             var customOnEnd = kwargs.onEnd;
             genro.dom.effect(domNode,'fadeout',{duration:duration,delay:delay,
                                onEnd:function(){
                                    domNode.innerHTML=null;if(customOnEnd){customOnEnd();}}});
        };
        pane._('span',mbKw);
    },
    slot_dashboardSaver:function(pane,slotValue,slotKw,frameCode){
        var kw = {title:_T('Save as dashboard item'),
            iconClass:'iconbox case',
            action:function(evt){
                var dashboardRoot =this.attributeOwnerNode('_dashboardRoot');
                if(dashboardRoot){
                    dashboardRoot.publish('saveDashboard');
                }
            }
        };
        pane._('slotButton',objectUpdate(kw,slotKw));
    }
});

dojo.declare("gnr.widgets.SelectionStore", gnr.widgets.gnrwdg, {
    contentKwargs: function(sourceNode, attributes) {
        if ('name' in attributes){
            attributes['_name'] = objectPop(attributes,'name');
        }
        if ('content' in attributes){
            attributes['_content'] = objectPop(attributes,'content');
        }
        //attributes['path'] = attributes['storepath'];
        attributes.columns = attributes.columns || '==gnr.getGridColumns(this);';
        attributes.sum_columns = attributes.sum_columns || '==this.store.getSumColumns();';
        attributes.method = attributes.method || 'app.getSelection';
        if (!('checkPermissions' in attributes)){
            attributes.checkPermissions = true;
        }
        if('chunkSize' in attributes && !('selectionName' in attributes)){
            attributes['selectionName'] = '*';
        }
        return attributes;
    },





    createContent:function(sourceNode, kw,children) {
        var chunkSize = objectPop(kw,'chunkSize',0);
        var storeType = objectPop(kw,'storeType') || (chunkSize? 'VirtualSelection':'Selection');
        kw.row_count = chunkSize;
        var identifier = objectPop(kw,'_identifier') || '_pkey';
        var _onError = objectPop(kw,'_onError');
        var deleteRows = objectPop(kw,'deleteRows');
        var allowLogicalDelete = objectPop(kw,'allowLogicalDelete');
        var linkedWidgetNode = objectPop(kw,'linkedWidgetNode');
        var skw = objectUpdate({_cleared:false},kw);
         //skw['_delay'] = kw['_delay'] || 'auto';
        skw.script="if(_cleared){this.store.clear();}else{if(this.form && this.form._reloadingAfterSave && !this.store.hasChanges()){return;}this.store.loadData();}";

        objectExtract(skw,'nodeId,_onCalling,_onResult,columns')
        var selectionStarter = sourceNode._('dataController',skw).getParentNode();

        objectExtract(kw,'_onStart,_cleared,_fired,_delay')
        var v;
        for (var k in kw){
           v = kw[k];
           if(typeof(v)=='string'){
               if(v[0]=='^'){
                   kw[k] = v.replace('^','=');
               }
           }
        }
        if(!'_POST' in kw){
            kw['_POST'] = true;
        }
        var selectionStore = sourceNode._('dataRpc',kw);
        //var cb = "this.store.onLoaded(result,_isFiredNode);";
        //selectionStore._('callBack',{content:cb});
        var rpcNode = selectionStore.getParentNode();
        rpcNode.attr['_onError'] = function(error,originalKwargs){
           if(_onError){
               funcApply(_onError,{error:error,kwargs:originalKwargs},rpcNode);
           }
           rpcNode.store.clear();
           rpcNode.store.gridBroadcast(function(grid){
                grid.sourceNode.publish('loadingData',{loading:false});
           });
        };
        var storeKw = {'identifier':identifier,'chunkSize':kw.row_count,
                       'storeType':storeType,'unlinkdict':kw.unlinkdict,
                       'deletemethod':kw.deletemethod,
                       'allowLogicalDelete':allowLogicalDelete,
                        'deleteRows':deleteRows,'linkedWidgetNode':linkedWidgetNode};
        if('startLocked' in kw){
            storeKw.startLocked = kw.startLocked;
        }
        var storeInstance = new gnr.stores[storeType](rpcNode,storeKw);
        rpcNode.store = storeInstance;
        selectionStarter.store = storeInstance;
        sourceNode.gnrwdg.store = storeInstance;
        return selectionStore;
     }
});

dojo.declare("gnr.widgets.BagStore", gnr.widgets.gnrwdg, {
     createContent:function(sourceNode, kw,children) {
        if(kw.data){
            kw.selfUpdate = kw.selfUpdate || false;
            kw.script = "this.store.loadData(data,selfUpdate);";
        }

        var identifier = objectPop(kw,'_identifier') || '_pkey';
        var storeType = objectPop(kw,'storeType') || 'ValuesBagRows';
        var deleteRows = objectPop(kw,'deleteRows');
        var store = sourceNode._('dataController',kw);
        var storeNode = store.getParentNode();
        storeNode.store = new gnr.stores[storeType](storeNode,{identifier:identifier,deleteRows:deleteRows});
        return store;
     },
     onChangedView:function(){
        return;
     }
});



dojo.declare("gnr.stores._Collection",null,{
    messages:{
        delete_one : "!!You are about to delete the selected record.<br/>You can't undo this",
        delete_logical_one : "!!The record cannot be removed.<br/>It will be hidden instead.",
        delete_many : "!!You are about to delete $count records.<br/>You can't undo this",
        delete_logical_many : "!!You are about to delete $count records <br/> Some of them cannot be deleted but will be hidden instead.",
        unlink_one:"!!You are about to remove the selected record from current $master",
        unlink_many:"!!You are about to discard the selected $count records from current $master",
        archive_one:"!!You are about to set archiviation date in the selected record",
        archive_many:"!!You are about to set archiviation date in the selected $count records"
    },
    
    constructor:function(node,kw){
        this.storeNode = node;
        this.storepath = this.storeNode.absDatapath(this.storeNode.attr.storepath);
        var startData = this.storeNode.getRelativeData(this.storepath,true);
        this.locked = null;
        this.inherithLock = false;
        this.inheritProtect = false;
        var deleteRows = objectPop(kw,'deleteRows');
        if (deleteRows){
            this.deleteRows = funcCreate(deleteRows,'pkeys,protectPkeys',this);
        }
        var startLocked= 'startLocked' in kw? objectPop(kw,'startLocked'):false;
        for (var k in kw){
            this[k] = kw[k];
        }
        var that = this;
        var cb = function(){
            that.storeNode.subscribe('setLocked',function(v){
                that.setLocked(v);
            });
            var parentForm = that.storeNode.attr.parentForm===false? false:that.storeNode.getFormHandler();
            if(parentForm){
                that.inherithLock = 'inherithLock' in that.storeNode.attr?  that.storeNode.attr.inherithLock:true;
                that.inheritProtect = 'inheritProtect' in that.storeNode.attr?  that.storeNode.attr.inheritProtect:true;
            }
            if(parentForm===false){
                startLocked = false;
                this.locked=false;
            }
            else if(that.inherithLock && parentForm){
                that.storeNode.registerSubscription('form_'+parentForm.formId+'_onDisabledChange',that,function(kwargs){
                    this.setLocked(kwargs.locked);
                });
            }
            dojo.subscribe('onPageStart',function(){
                startLocked = parentForm?parentForm.isDisabled():startLocked;
                that.setLocked(startLocked);
            });
        };
        genro.src.onBuiltCall(cb);

    },


    setNewStorepath:function(newstorepath){
        this.storeNode.attr.storepath = newstorepath;
        this.storepath = this.storeNode.absDatapath(this.storeNode.attr.storepath);
        var storepath = this.storepath;
        var that = this;
        this.gridBroadcast(function(grid){
            grid.sourceNode.attr.storepath = storepath;
            if(grid.gridEditor){
                grid.gridEditor.applyStorepath();
            }
            grid.newDataStore();
        });
    },

    getSumColumns:function(){
        return ;
    },

    clear:function(){
        this.storeNode.setRelativeData(this.storepath,
                                        new gnr.GnrBagNode(null, '', new gnr.GnrBag(), {}),
                                        null,null,'loadData');
    },

    gridBroadcast:function(cb){
        this.linkedGrids().forEach(cb);
    },

    setBlockingReason:function(reason,doset){
        this._blocking_reasons = this._blocking_reasons || {};
        if(doset=='toggle'){
            doset = !(reason in this._blocking_reasons);
        }
        if(doset===true){
            this._blocking_reasons[reason] = true;
        }else if(doset===false){
            objectPop(this._blocking_reasons,reason);
        }
    },

    isEnabledStore:function() {
        this._blocking_reasons = this._blocking_reasons || {};
        return !objectNotEmpty(this._blocking_reasons) && (this.hasVisibleClients() || this.loadInvisible);
    },

    hasVisibleClients:function(){
        if (this.linkedWidgetNode){
            return this.linkedWidgetNode.gnrwdg.isVisible();
        }
        return this.linkedGrids().some(function(grid){
            return genro.dom.isVisible(grid.sourceNode);
        });
    },

    runQuery:function(cb,runKwargs){
        var result =  this.storeNode.fireNode(runKwargs);
        if(result instanceof dojo.Deferred){
            result.addCallback(function(r){
                cb(r)
            });
        }else{
            result = cb(result);
        }
        return result;
    },



    onLoading:function(){

    },

    onLoaded:function(result){
        this.storeNode.setRelativeData(this.storepath,result,null,null,'loadData');
        return result;
    },

    onChangedView:function(){
        return;
    },
    loadData:function(){
        return;
    },

    onStartEditItem:function(form){
        this._editingForm = form;
    },

    onEndEditItem:function(form){
        this._editingForm = false;
    },

    currentPkeys:function(){
        console.warn('currentPkeys not implemented in this store',this);
        return null;
    },

    setLocked:function(value){
        if(value=='toggle'){
            value = !this.locked;
        }
        this.locked = value;
        var parentForm = this.storeNode.getFormHandler();
        var parentProtect = (parentForm && this.inheritProtect)?parentForm.isProtectWrite():false;
        this.storeNode.setRelativeData('.locked',value);
        this.storeNode.setRelativeData('.disabledButton',value || parentProtect);
        this.storeNode.publish('onLockChange',{'locked':this.locked});
    },
    
    
    deleteRows:function(pkeys,protectPkeys){
        return;
    },
    duplicateRows:function(pkeys){},

    archiveRows:function(){
        console.error('archiveRows not implemented')
    },

    archiveAsk:function(pkeys,protectPkeys,cb){
        var count = pkeys.length;
        var cb = cb || this.archiveRows; 
        if(count==0){
            return;
        }
        var dlg = genro.dlg.quickDialog('Alert',{_showParent:true,width:'280px'});
        var msg = count==1?'one':'many';
        dlg.center._('div',{innerHTML:_T(this.messages['archive_'+msg]).replace('$count',count), 
                            text_align:'center',_class:'alertBodyMessage'});
        var that = this;
        var slotbar = dlg.bottom._('slotBar',{slots:'*,cancel,archive',
                                                action:function(){
                                                    dlg.close_action();
                                                    if(this.attr.command=='archiveRows'){
                                                        cb.call(that,pkeys,protectPkeys,genro.getData('gnr._dev.archiveAsk.date'));
                                                    }
                                                }});
        slotbar._('button','cancel',{label:_T('Cancel'),command:'cancel'});
        var btnattr = {label:_T('Confirm'),command:'archiveRows'};
        var fb = genro.dev.formbuilder(dlg.center,1,{border_spacing:'1px',width:'100%',margin_bottom:'12px'});
        genro.setData('gnr._dev.archiveAsk.date',genro.getData('gnr.workdate'));
        fb.addField('dateTextBox',{value:'^gnr._dev.archiveAsk.date',width:'8em',lbl_text_align:'right',
                                        lbl:_T('Date'),lbl_color:'#444',parentForm:false});
        if(count>1){
            fb.addField('numberTextBox',{value:'^gnr._dev.archiveAsk.count',width:'5em',lbl_text_align:'right',
                                        lbl:_T('N.Records'),lbl_color:'#444',parentForm:false});
            btnattr['disabled']='==_count!=_tot;';
            btnattr['_tot'] = count;
            fb._('data',{path:'gnr._dev.archiveAsk.count',content:null});
            btnattr['_count'] = '^gnr._dev.archiveAsk.count';
        }
        slotbar._('button','archive',btnattr);
        dlg.show_action();   
    },

    deleteAsk:function(pkeys,protectPkeys,deleteCb){        
        var count = pkeys.length;
        var deleteCb = deleteCb || this.deleteRows; 
        if(count==0){
            return;
        }
        var dlg = genro.dlg.quickDialog('Alert',{_showParent:true,width:'280px'});
        var msg = count==1?'one':'many';
        var del_type,master;
        if(this.unlinkdict){
            del_type = 'unlink';
            master = _T(this.unlinkdict.one_name);
        }else{
            del_type = 'delete';
            master ='';
            if(this.allowLogicalDelete && protectPkeys){
                del_type = 'delete_logical';
            }
        }
        dlg.center._('div',{innerHTML:_T(this.messages[del_type+'_'+msg]).replace('$count',count).replace('$master',master), 
                            text_align:'center',_class:'alertBodyMessage'});
        var that = this;
        var slotbar = dlg.bottom._('slotBar',{slots:'*,cancel,delete',
                                                action:function(){
                                                    dlg.close_action();
                                                    if(this.attr.command=='deleteRows'){
                                                        deleteCb.call(that,pkeys,protectPkeys);
                                                    }
                                                }});
        slotbar._('button','cancel',{label:_T('Cancel'),command:'cancel'});
        var btnattr = {label:_T('Confirm'),command:'deleteRows'};
        if(count>1){
            var fb = genro.dev.formbuilder(dlg.center,1,{border_spacing:'1px',width:'100%',margin_bottom:'12px'});
            fb.addField('numberTextBox',{value:'^gnr._dev.deleteask.count',width:'5em',lbl_text_align:'right',
                                        lbl:_T('Records to delete'),lbl_color:'#444',parentForm:false});
            btnattr['disabled']='==_count!=_tot;';
            btnattr['_tot'] = count;
            fb._('data',{path:'gnr._dev.deleteask.count',content:null});
            //genro.setData('gnr._dev.deleteask.count',null);
            btnattr['_count'] = '^gnr._dev.deleteask.count';
        }
        
        slotbar._('button','delete',btnattr);
        dlg.show_action();
    },
    
    onCounterChanges:function(counterField,changes){},
    
    getData:function(filtered){
        var result = this.storeNode.getRelativeData(this.storepath);
        if(!result){
            result = new gnr.GnrBag();
            this.storeNode.setRelativeData(this.storepath,result,null,null,'loadData');
        }
        if(!(filtered && this._filtered)){
            return result;
        }
        var filteredResult = new gnr.GnrBag();
        var fn;
        this._filtered.forEach(function(nodeIdx){
            fn = result.getNode('#'+nodeIdx);
            filteredResult.setItem(fn.label,fn._value instanceof gnr.GnrBag?fn._value.deepCopy():fn._value,objectUpdate({},fn.attr));
        });
        return filteredResult;
    },

    
    getItems:function(){
        return this.getData()._nodes;
    },
    len:function(filtered){
        if(filtered && this._filtered){
            return this._filtered.length;
        }
        return this.getItems().length || 0;
    },
    sum:function(field){
        
    },
    
    indexByCb:function(cb,backward){
        var n = this.len(true);
        for (var i = 0; i < n; i++) {
            var k_i = backward?n-i:i;
            if (cb(this.rowByIndex(k_i))) {
                return k_i;
            }
        }
        return -1;
    },
    
    absIndex:function(idx,reverse){
        //if (this.invalidFilter()) {
        //    console.log('invalid filter');
        //}
        if(!this._filtered){
            return idx;
        }

        return reverse ? dojo.indexOf(this._filtered,idx):this._filtered[idx];
    },
    
    getKeyFromIdx:function(idx,filtered){
        var data = this.getData();
        if(!data){
            return;
        }
        var item;
        data=data.getNodes();
        if ((idx<0)||( idx>(data.length-1))){
            return null;
        } 
        if(filtered && this._filtered){
            idx = this._filtered[idx];
        }   
        return this.keyGetter(data[idx]);
    },
    getIdxFromPkey:function(pkey,fiteredIndex){
        var result = -1;
        var data = this.getData();
        var that = this;
        if(pkey && data){
            data=data.getNodes();
            var k = -1;
            dojo.some(data,function(n){
                k++;
                if(that.keyGetter(n)==pkey){
                    result = k;
                    return true;
                }
            });
            if(fiteredIndex!==false && result>=0 && this._filtered){
                return this._filtered.indexOf(result);
            }
            return result;
        }
    },
    rowBagNodeByIdentifier:function(pkey){
        var idx = this.getIdxFromPkey(pkey);
        if(idx>=0){
            return this.itemByIdx(idx);
        }
    },

    rowByIndex:function(idx,bagFields){
        var rowdata={};
        var node=this.itemByIdx(idx);
        if (node){
            this.setExternalChangeClasses(node);
            return this.rowFromItem(node,bagFields);
        }
        return rowdata;
    },

    setExternalChangeClasses:function(node){

    },
    
    filterToRebuild: function(value) {
        this._filterToRebuild=value;
    },
    invalidFilter: function() {
        return this._filterToRebuild;
    },
    resetFilter: function() {
        return this._filtered = null;
    },
    isFiltered:function(){
        return this._filtered !==null;
    },
    
    compileFilter:function(grid,value,filterColumn,colType){
        var cbsearch;
        var cb;
        if(!isNullOrBlank(value)){
            if (colType in {'A':null,'T':null}) {
                var regexp = new RegExp(value, 'i');
                cbsearch = function(rowdata, index, array) {
                    return regexp.test(grid.getRowText(index,' ',filterColumn.split('+'),true));
                };
            } else {
                var toSearch = /^(\s*)([\<\>\=\!\#]+)(\s*)(.+)$/.exec(value);
                if (toSearch) {
                    var val;
                    var op = toSearch[2];
                    if (op == '=') {op = '==';}
                    if ((op == '!') || (op == '#')) {op = '!=';}
                    if (colType in {'R':null,'L':null,'I':null,'N':null}) {
                        val = dojo.number.parse(toSearch[4]);
                    } else if (colType == 'D') {
                        val = dojo.date.locale.parse(toSearch[4], {formatLength: "short",selector:'date'});
                    } else if (colType == 'DH') {
                        val = dojo.date.locale.parse(toSearch[4], {formatLength: "short"});
                    }                
                    cbsearch = function(rowdata, index, array) {
                        return genro.compare(op,rowdata[filterColumn],val);
                    };
                }
            }
        }
        if(grid.filterManager && grid.filterManager.hasActiveFilter()){
            cb = function(rowdata, index, array){
                return grid.filterManager.isInFilterSet(rowdata) && (cbsearch?cbsearch(rowdata, index, array):true);
            };
        }else{
            cb = cbsearch;
        }
        return cb;
    },

    createFiltered:function(grid,currentFilterValue,filterColumn,colType){
        var cb = this.compileFilter(grid,currentFilterValue,filterColumn,colType);
        if (!cb && !grid.excludeListCb){
            this._filtered = null;
            return null;
        }
        var filtered=[];
        var filteringList = null;

        if (grid.excludeListCb) {
            filteringList = grid.excludeListCb.call(this.storeNode);
        }
        var filteringMode = grid.filteringMode || 'exclude';
        var that = this;
        var sn = grid.sourceNode
        sn.__evaluated_attrs = sn.evaluateOnNode(sn.attr)
        dojo.forEach(this.getItems(), 
                    function(n,index,array){
                        var rowdata = that.rowFromItem(n);
                        var result = cb? cb.apply(sn, [rowdata,index,array]):true; 
                        var include;
                        if(result){
                            if(filteringMode=='exclude'){
                                include =  ((!filteringList)||(dojo.indexOf(filteringList, rowdata[grid.excludeCol]) == -1));
                            }else if(filteringMode=='disabled'){
                                include = true;
                            }else{
                                include =filteringList && (dojo.indexOf(filteringList, rowdata[grid.excludeCol]) >= 0);
                            }
                            if(include){
                                filtered.push(index);
                            }
                        }
                    });
        this._filtered=filtered;
        this._filterToRebuild=false;
    },
    linkedGrids:function(){
        if(this._linkedGrids){
            return this._linkedGrids;
        }
        var result= [];
        var storeCode;
        var storeNodeId = this.storeNode.attr.nodeId;
        genro.src._main.walk(function(n){
            if(n.widget && n.widget.selectionKeeper){
                storeCode = n.attr.store || n.attr.nodeId;
                if(storeCode+'_store'==storeNodeId){
                    result.push(n.widget);
                }
            }
        },'static');
        this._linkedGrids = result;
        return result;
    },


    hasErrors:function(){
        //to implement
    },
    hasChanges:function(){
        //to implement
    }
});

dojo.declare("gnr.stores.BagRows",gnr.stores._Collection,{
    loadData:function(data,selfUpdate){
        if(selfUpdate){
            dojo.forEach(this.linkedGrids(),function(grid){
                grid.selectionKeeper('save');
                grid._batchUpdating = true;
            });
        }
        data = data?data.deepCopy(): new gnr.GnrBag();
        this.storeNode.setRelativeData(this.storepath,data,null,null,'loadData');
        if(this.sortedBy){
            this.sort();
        }
        if(selfUpdate){
            dojo.forEach(this.linkedGrids(),function(grid){
                grid.applyFilter(true);
                grid._batchUpdating = false;
                grid.restoreSelectedRows();
            });
        }
    },


    getRowByIdx:function(idx){
        return ;
    },
    getItems:function(){
        var data=this.getData();
        return data?data.getNodes():[];
    },

    deleteRows:function(pkeys,protectPkeys){
        var data = this.getData()
        this.gridBroadcast(function(grid){
            grid.selection.unselectAll()
        });
        var that = this;
        pkeys.forEach(function(n){
            data.popNode(n);
        });
        this.linkedGrids().forEach(function(grid){
            grid.sourceNode.publish('onDeletedRows',{pkeys:pkeys,protectPkeys:protectPkeys})
        });

    },

    itemByIdx:function(idx){
        var item=null;
        if (idx >= 0) {
            idx = this.absIndex(idx);
            var nodes=this.getItems();
            if (idx <= this.len()) {
                item=nodes[idx];
            }
        }
        return item;
    },
    updateRow:function(idx,updDict){
        var rowNode = this.itemByIdx(idx);
        if(rowNode){
            return this.updateRowNode(rowNode,updDict);
        }
    },

    filteredRowsIndex:function(filteringObject){
        var items = this.getItems();
        var r;
        var result = [];
        for (var i = 0; i < items.length; i++) {
            if(objectIsContained(filteringObject,this.rowFromItem(items[i]))){
                result.push(i);
            }
        };
        return result;
    },
    hasChanges:function(){
        var data = this.getData()
        if(data.getNodeByAttr('_newrecord')){
            return true
        }
        return this.getData().getNodeByAttr('_loadedValue')!=null;
    },

    hasErrors:function(){
        return this.getData().getNodeByAttr('_validationError')!=null;
    }
});

dojo.declare("gnr.stores.ValuesBagRows",gnr.stores.BagRows,{
    rowFromItem:function(item,bagFields){
        var result = objectUpdate({},item.attr);
        var value = item.getValue();
        if (value) {
            var v;
            value.forEach(function(n){
                v = n.getValue();
                if(v instanceof gnr.GnrBag){
                    v = bagFields?v:null;
                }
                result[n.label] = v;
            })
        }
        result[this.identifier] = isNullOrBlank(result[this.identifier])? item.label:result[this.identifier];

        return result;
    },

    updateRowNode:function(rowNode,updDict){
        var rowData = rowNode.getValue();
        var idx = this.getData().index(rowNode.label);
        for(var k in updDict){
            var n = rowData.getNode(k,'static');
            if(!n){
                //put the missing node
                rowData.setItem(k,null,null,{doTrigger:false});
            }
            rowData.setItem(k,updDict[k],null,{doTrigger:{editedRowIndex:idx},lazySet:true});
        }
    },

    keyGetter :function(n){
        return this.rowFromItem(n)[this.identifier];
    },

    sort:function(sortedBy){
        this.sortedBy = sortedBy || this.sortedBy;
        if(!this.sortedBy){
            return;
        }
        var data = this.getData();
        var sl = [];
        dojo.forEach(this.sortedBy.split(','),function(n){
            sl.push(n);
        });
        sl = sl.join(',');
        data.sort(sl);
    },

    onCounterChanges:function(counterField,changes){},

    sum:function(field){
        return this.getData().sum('#v.'+field); 
    }

});


dojo.declare("gnr.stores.AttributesBagRows",gnr.stores.BagRows,{
    rowFromItem:function(item,bagFields){
        var result = objectUpdate({},item.attr);
        if(!bagFields){
            for(var k in result){
                if(isBag(result[k])){
                    objectPop(result,k);
                }
            }
        }
        result[this.identifier] = isNullOrBlank(result[this.identifier])? item.label:result[this.identifier];
        return result;
    },
    updateRowNode:function(rowNode,updDict){
        var idx = this.getData().index(rowNode.label);
        rowNode.updAttributes(updDict,{editedRowIndex:idx});
    },
    keyGetter :function(n){
        return n.attr[this.identifier];
    },

    sort:function(sortedBy){
        this.sortedBy = sortedBy || this.sortedBy;
        if(!this.sortedBy){
            return;
        }
        var data = this.getData();
        var sl = [];
        dojo.forEach(this.sortedBy.split(','),function(n){
            if(n.slice(0,3)!='#a.'){
                n = '#a.'+n;
            }
            sl.push(n);
        });
        sl = sl.join(',');
        data.sort(sl);
    },

    sum:function(field){
       return this.getData().sum('#a.'+field); 
    }
});

dojo.declare("gnr.stores.RpcBase",gnr.stores.AttributesBagRows,{
    askToDelete:true,
    loadData:function(){
        var that = this;
        if(!this.isEnabledStore()){
            this.storeNode.watch('isEnabledStore',function(){
                return that.isEnabledStore();
            },function(){
                that.loadingDataDo();
            });
            return;
        }
        return this.loadingDataDo();
    },

    loadingDataDo:function(){
        var that = this;
        this.loadingData = true;
        this.gridBroadcast(function(grid){
            grid.selectionKeeper('save');
            grid.sourceNode.publish('loadingData',{loading:true});
        });
        var cb = function(result){
            that.resetFilter();
            that.onLoaded(result);
            that.loadingData = false;
            that.gridBroadcast(function(grid){
                grid.sourceNode.publish('loadingData',{loading:false});
            });
        };
        this.onLoading();
        return this.runQuery(cb);
    },

    onDeletedRows:function(pkeys){
        return this.loadData()
    },

    deleteRows:function(files,protectPkeys){
        var that = this;
        var unlinkfield = this.unlinkdict?this.unlinkdict.field:null;
        var rpcdelete = this.deletemethod;
        genro.assert(rpcdelete,'missing delete rpc')
        genro.serverCall(rpcdelete,{files:files},function(result){
            that.onDeletedRows(files);
        },null,'POST');
    },

});


dojo.declare("gnr.stores.FileSystem",gnr.stores.RpcBase,{
    askToDelete:true,
    deleteRows:function(files,protectPkeys){
        var that = this;
        var unlinkfield = this.unlinkdict?this.unlinkdict.field:null;
        var rpcdelete = this.deletemethod || 'app.deleteFileRows';
        genro.serverCall(rpcdelete,{files:files},function(result){
            that.onDeletedRows(files);
        },null,'POST');
    }
});


dojo.declare("gnr.stores.Selection",gnr.stores.AttributesBagRows,{
    askToDelete:true,
    constructor:function(){
        var liveUpdate = this.storeNode.attr.liveUpdate || 'LOCAL';
        var liveUpdateExcludeReason = this.storeNode.getAttributeFromDatasource('liveUpdateExcludeReason');

        if(liveUpdate=='NO'){
            return;
        }
        var that = this;
        this.pendingChanges = [];
        this.lastLiveUpdate = new Date()
        this._editingForm = false;
        this.loadInvisible = this.storeNode.getAttributeFromDatasource('loadInvisible');
        this.liveUpdateDelay = this.storeNode.getAttributeFromDatasource('liveUpdateDelay');
        this.externalLiveUpdateDelay = this.storeNode.getAttributeFromDatasource('externalLiveUpdateDelay');
        this.liveUpdateUnattended = this.storeNode.getAttributeFromDatasource('liveUpdateUnattended');
        var cb = function(){
            that.storeNode.registerSubscription('dbevent_'+that.storeNode.attr.table.replace('.','_'),that,
            function(kw){
                var from_page_id = kw.changeattr.from_page_id;
                var dbevent_reason = kw.changeattr.dbevent_reason;
                if(liveUpdateExcludeReason && liveUpdateExcludeReason==dbevent_reason){
                    return;
                }
                if(liveUpdate=='PAGE'){
                    if(genro.page_id!=from_page_id){
                        return;
                    }
                }
                if(liveUpdate=='LOCAL'){
                    if(!genro.isLocalPageId(from_page_id)){
                        return;
                    }
                }
                if(that.freezedStore()){
                    return;
                }
                var isExternal = from_page_id!=genro.page_id;
                dojo.forEach(kw.changelist,function(c){
                    c._isExternal = isExternal;
                    that.pendingChanges.push(c);
                });
                that.storeNode.watch('externalChangesDisabled',function(){
                    if(that._editingForm || that.loadInvisible){
                        return genro.dom.isWindowVisible();
                    }
                    if(that.storeNode.form && that.storeNode.form.opStatus){
                        return false;
                    }
                    var currDelay = isExternal?that.externalLiveUpdateDelay:that.liveUpdateDelay;
                    var doUpdate = currDelay && that.lastLiveUpdate?(new Date()-that.lastLiveUpdate)/1000>currDelay:true;
                    if(doUpdate && !that.liveUpdateUnattended){
                        doUpdate = (genro._lastUserEventTs > that.lastLiveUpdate) || ((new Date()-that.lastLiveUpdate)/1000)>60;
                    }
                    return that.hasVisibleClients() && doUpdate;
                },function(){
                    that.lastLiveUpdate = new Date();
                    var changelist = that.pendingChanges;
                    that.pendingChanges = [];
                    if(changelist.length>0){
                        if(that.storeNode.attr.groupByStore){
                            //avoid checking in groupby
                            that.loadData();
                        }else{
                            that.onExternalChange(changelist);    
                        }
                    }
                });
            });};
            genro.src.onBuiltCall(cb);
    },

    getSumColumns:function(){
        var sum_columns = this.storeNode.getRelativeData('.sum_columns');
        sum_columns = sum_columns?sum_columns.split(','):[];
        this.linkedGrids().forEach(function(grid){
            if(grid.sourceNode._serverTotalizeColumns && !grid.gridEditor){
                for (var field in grid.sourceNode._serverTotalizeColumns){
                    arrayPushNoDup(sum_columns,field);
                }
            }
        });
        return sum_columns.join(',');
    },

    loadData:function(runKwargs){
        var that = this;
        this.pendingLoading = true;
        if(!(this.isEnabledStore())){
            this.storeNode.watch('isEnabledStore',function(){
                return that.isEnabledStore();
            },function(){
                that.loadingDataDo(runKwargs);
            });
            return;
        }
        this.loadingDataDo(runKwargs);
    },

    loadingDataDo:function(runKwargs){
        var that = this;
        this.loadingData = true;
        this.gridBroadcast(function(grid){
            grid.sourceNode.publish('loadingData',{loading:true});
        });
        var cb = function(result){
            that.resetFilter();
            that.onLoaded(result);
            that.loadingData = false;
            that.gridBroadcast(function(grid){
                grid.sourceNode.publish('loadingData',{loading:false});
            });
        };
        this.onLoading();
        return this.runQuery(cb,runKwargs);
    },

    cleanColumns:function(cols){
        var result = {};
        if(!cols){
            return;
        }
        cols.split(',').forEach(function(n){
            n = n.toLowerCase();
            if(n.indexOf(' as ')>=0){
                n = n.split(' as ')[1]
            }else{
                n = n.trim().split(' ')[0].replace('$','').replace(/\./g, '_').replace(/@/g, '_');
            }
            result[n] = true;
        });
        return result;
    },

    onChangedView:function(){
        var data = this.getData();
        var n = this.len(true)-1;
        if(n>=0){
            var k = 0;
            var dataColumns = {};
            do{
                dataColumns = this.rowByIndex(k,true);
                k++;
            }while(k<=n && ('_newrecord' in dataColumns))
            if('_newrecord' in dataColumns){
                // do not reload data if there are new rows
                return;
            }
            gnr.getGridColumns(this.storeNode);
            var newColumns = this.cleanColumns(this.storeNode._currentColumns);
            var previousColumns = this.cleanColumns(this.storeNode._previousColumns);
            var addedColumns = [];            
            for(var k in newColumns){
                if(k in previousColumns){
                    objectPop(previousColumns,k);
                }else{
                    addedColumns.push(k);
                }
            }
            if(addedColumns.length>0){
                this.loadData();
            }else if(this.storeNode.attr.groupByStore && objectNotEmpty(previousColumns)){
                for(var k in previousColumns){
                    if(!['_avg','_sum','_min','_max'].some(function(aggr){return k.endsWith(aggr);})){
                        this.loadData();
                        return;
                    }
                }
            }
        }
    },


    currentPkeys:function(caption_field){
        var data = this.getData();
        var result = [];
        var r;
        data.forEach(function(n){
            r = n.attr;
            result.push(caption_field? {'pkey':r['_pkey'],'caption':r[caption_field]} : r['_pkey']);
        });
        return result;
    },

    freezedStore:function(){
        if(this.freezed){
            return true;
        }
        var if_condition = this.storeNode.attr._if;
        if(if_condition){
            var if_result = funcApply('return '+if_condition,this.storeNode.currentAttributes(),this.storeNode);
            if(!if_result){
                return true;
            }
        }
        return false;
    },
    
    onExternalChange:function(changelist){
        var eventdict = {};
        var dbevt,pkeys,wasInSelection,willBeInSelection;
        var insOrUpdKeys = [];
        var delKeys = [];
        var data = this.getData();
        var that = this;
        if(!data){
            return;
        }
        var isExternalDict = {};
        dojo.forEach(changelist,function(change){
            if (change['dbevent']=='D'){
                if (dojo.indexOf(delKeys,change.pkey)<0){
                     delKeys.push(change.pkey);
                }
               
            }else{
                if (dojo.indexOf(insOrUpdKeys,change.pkey)<0){
                    insOrUpdKeys.push(change.pkey);
                    if(change._isExternal){
                        isExternalDict[change.pkey] = change._isExternal;
                    }
                }
                if(change.old_pkey && change.old_pkey!=change.pkey){
                    var changedNode = data.getNodeByAttr('_pkey',change.old_pkey);
                    if(changedNode){
                        changedNode.attr['_pkey'] = change.pkey;
                    }
                }
            }
        });

        if (insOrUpdKeys.length>0) {
            var original_condition =  this.storeNode.attr.condition;
            var newcondition = ' ( $pkey IN :store_chpkeys ) ';
            var chpkeys = insOrUpdKeys;
            var condition = original_condition?original_condition+' AND '+newcondition:newcondition;
            if(this.freezedStore()){
                return;
            }
            this.runQuery(function(result){
                                            willBeInSelection={};
                                            result.getValue().forEach(function(n){
                                                willBeInSelection[n.attr['_pkey']] = n;
                                            },'static');
                                            that.checkExternalChange(delKeys,insOrUpdKeys,willBeInSelection,isExternalDict);
                                            return result;
                                    },{store_chpkeys:chpkeys,condition:condition,applymethod:null});


        }else if (delKeys.length>0) {
            this.checkExternalChange(delKeys,[],[],isExternalDict);
        }
    },
    
    onCounterChanges:function(counterField,changes){
        genro.serverCall('app.counterFieldChanges',{table:this.storeNode.attr.table,counterField:counterField,changes:changes});
    },
    
    
    checkExternalChange:function(delKeys,insOrUpdKeys,willBeInSelection,isExternalDict){
        var linkedGrids = this.linkedGrids();
        var selectedPkeysDict = {};
        var selectedIndex,selectedPkey;
        var data = this.getData();
        dojo.forEach(linkedGrids,function(grid){
            //grid.batchUpdating(true);
            genro.dom.removeClass(grid.sourceNode,'onExternalChanged');
            selectedIndex = grid.selection.selectedIndex;
            if(selectedIndex!=null&&selectedIndex>=0){
                selectedPkey = grid.rowIdByIndex(selectedIndex);
                selectedPkeysDict[selectedPkey] = selectedPkeysDict[selectedPkey] || [];
                selectedPkeysDict[selectedPkey].push(grid);
            }
            grid._saved_selections = grid.selectionKeeper('save');
        });
        var changedRows = {};
       
        var that = this;
        var toUpdate = false;
        var wasInSelectionNode,willBeInSelectionNode,pkey;
        this.externalChangedKeys = this.externalChangedKeys || {};
        var wasInSelectionCb = function(pkeys){
            var result = {};
            data.forEach(function(n){
                if (dojo.indexOf(pkeys,n.attr._pkey)>=0){
                    result[n.attr._pkey] = n;
                }
            },'static');  
            return result;
        };
        var insOrUpdKeys_wasInSelection=wasInSelectionCb(insOrUpdKeys);
        var delKeys_wasInSelection=wasInSelectionCb(delKeys);
        var changeCount = objectSize(willBeInSelection) + objectSize(insOrUpdKeys_wasInSelection) + objectSize(delKeys_wasInSelection);
        var rt = this.reload_treshold || 0.3;
        var sum_columns = this.storeNode.getAttributeFromDatasource('sum_columns');
        var applymethod = this.storeNode.getAttributeFromDatasource('applymethod');
        var fullReloadOnChange = this.storeNode.getAttributeFromDatasource('fullReloadOnChange');
        if(changeCount>0 && ((changeCount>this.len()*rt) || sum_columns || fullReloadOnChange || applymethod)){
            this.loadData();
            return
        }
        if(delKeys.length>0){
             for(pkey in delKeys_wasInSelection){
                 toUpdate = true;
                 data.popNode(delKeys_wasInSelection[pkey].label);
            }
        }
        if(insOrUpdKeys.length>0){
            dojo.forEach(insOrUpdKeys,function(pkey){
                wasInSelectionNode = insOrUpdKeys_wasInSelection[pkey];
                willBeInSelectionNode = willBeInSelection[pkey];
                if(wasInSelectionNode){
                    toUpdate=true;
                    if (willBeInSelectionNode) {
                        var rowNode = data.getNodeByAttr('_pkey',willBeInSelectionNode.attr._pkey);
                        var rowValue = rowNode.getValue('static');
                        var newattr = objectUpdate({},willBeInSelectionNode.attr);
                        if(pkey in isExternalDict){
                            for(var attrname in willBeInSelectionNode.attr){
                                changedRows[rowNode.attr._pkey] = rowNode;
                                if(!isEqual(rowNode.attr[attrname],willBeInSelectionNode.attr[attrname])){
                                    if(rowValue instanceof gnr.GnrBag){
                                        var editedNode = rowValue.getNode(attrname);
                                        if(editedNode){
                                            editedNode.updAttributes({'_loadedValue':objectPop(newattr,attrname)},false);
                                        }
                                    }
                                    if(attrname in newattr){
                                        newattr['_customClass_'+attrname] = 'externalChangedCell';
                                    }
                                 }else if(rowValue instanceof gnr.GnrBag){
                                     var editedNode = rowValue.getNode(attrname);
                                     if(editedNode){
                                        editedNode.updAttributes({'_loadedValue':objectPop(newattr,attrname)},false);
                                     }
                                 }
                            }
                        }
                        rowNode.updAttributes(newattr,true);
                        if(selectedPkeysDict[pkey]){
                            dojo.forEach(selectedPkeysDict[pkey],function(grid){
                                grid.sourceNode.publish('updatedSelectedRow');
                            });
                        }
                    }else{
                        data.popNode(wasInSelectionNode.label);
                    }
                }else if(willBeInSelectionNode){
                    toUpdate = true;
                    //if(isExternalChange){
                    //    that.externalChangedKeys[pkey] = true;
                    //}
                    data.setItem('#id',willBeInSelectionNode);
                }
            });
        }
        if(toUpdate && this.sortedBy){
            this.mustBeSorted = true;
        } 
        var that = this;
        dojo.forEach(linkedGrids,function(grid){
            //grid.batchUpdating(false);   
            if(toUpdate){
                if (!grid.gnrediting){
                    if(that.mustBeSorted){
                        that.sort();
                        if(that._filtered){
                            that.filterToRebuild(true);
                        }
                        that.mustBeSorted = false;
                    }
                    grid.updateRowCount('*');
                }else{
                    grid.pendingSort = true;
                }

                grid.restoreSelectedRows();
            }
            for (var k in changedRows){
                var n = changedRows[k];
                objectExtract(n.attr,'_customClass_*');
                if(grid.gridEditor){
                    grid.gridEditor.onExternalChange(k);
                }
            }
            genro.userInfoCb.push(function(){
                genro.dom.addClass(grid.sourceNode,'onExternalChanged');
            });
            grid.sourceNode.publish('onExternalChanged');
        });

    },

    duplicateRows:function(pkeys){
        var lockreason = this.storeNode.attr.nodeId+'_'+'deletingDbRows';
        var that = this;
        const n_records = pkeys.length;
        genro.dlg.ask(_T('Duplicate rows'),_T("You are going to duplicate")+' '+n_records+' ' +_T('records'),null,{
            confirm:function(){
                genro.lockScreen(true,lockreason,{thermo:true});
                genro.serverCall('app.duplicateDbRows',{pkeys:pkeys,table:that.storeNode.attr.table,
                                                    _sourceNode:that.storeNode,timeout:0},function(result){
                    genro.lockScreen(false,lockreason,'duplicatingRecords');
                },null,'POST');
           }
        });
    },

    deleteRows:function(pkeys,protectPkeys){
        var that = this;
        var unlinkfield = this.unlinkdict?this.unlinkdict.field:null;
        var lockreason = this.storeNode.attr.nodeId+'_'+'deletingDbRows';
        genro.lockScreen(true,lockreason,{thermo:true});
        genro.serverCall('app.deleteDbRows',{pkeys:pkeys,table:this.storeNode.attr.table,
                                             unlinkfield:unlinkfield,protectPkeys:protectPkeys,
                                            _sourceNode:this.storeNode,timeout:0},function(result){
            genro.lockScreen(false,lockreason,'deletingDbRows');
            that.onDeletedRows(result);
        },null,'POST');
    },

    archiveRows:function(pkeys,protectPkeys,date){
        var that = this;
        var unlinkfield = this.unlinkdict?this.unlinkdict.field:null;
        genro.serverCall('app.archiveDbRows',{pkeys:pkeys,table:this.storeNode.attr.table,archiveDate:date,
                                             unlinkfield:unlinkfield,protectPkeys:protectPkeys,
                                            _sourceNode:this.storeNode},function(result){
            that.onDeletedRows(result); //same action than delete
        },null,'POST');
    },

    onDeletedRows:function(result){
        var that = this;
        this.gridBroadcast(function(grid){
            genro.callAfter(function(){
                grid.updateCounterColumn();
            },300,grid,that.storeNode.attr.nodeId);
        });
    },

    onLoading:function(){
        this.pendingChanges = []; 
        this.externalChangedKeys = null;
    },

    onLoaded:function(result){
        delete this.pendingLoading;
        this.storeNode.setRelativeData(this.storepath,result,null,null,'loadData');
        return result;
    }
});


dojo.declare("gnr.stores.VirtualSelection",gnr.stores.Selection,{
    askToDelete:true,
    constructor:function(){
        this.pendingPages = {};
        this.lastIdx =0;
    },
    sort:function(){
        //override the standard sort because it has been sorted on the server
        //and does not work with paged store
        return;
    },
    len:function(filtered){
        var data = this.getData();
        if(!data){
            return 0;
        }
        var dataNode = data.getParentNode();
        if(!dataNode){
            return 0;
        }
        var len = dataNode.attr['totalrows'] || 0;
        if(!filtered){
            len = dataNode.attr['totalRowCount']||len;
        }
        return len;
    },
    
    onLoaded:function(result){
        if (result==null){
            console.warn('missing result')
            return
        }
        if(result.error){
            return;
        }
        this.clearBagCache();
        var selection = result.getValue(); 
        var data = new gnr.GnrBag();
        var resultattr = result.attr;
        data.setItem('P_0',result.getValue(),{pageIdx:0}); 
        this.rowtotal = resultattr.rowcount;
        this.totalRowCount = resultattr.totalRowCount;
        this.selectionName = resultattr.selectionName;
        this.storeNode.setRelativeData(this.storepath,data,resultattr,null,'loadData');
        if(resultattr.prevSelectedIdx && resultattr.prevSelectedIdx.length>0){
            var pagetoload = {};
            var cs = this.chunkSize;
            dojo.forEach(resultattr.prevSelectedIdx,function(idx){
                pagetoload[(idx - idx % cs) / cs]=true;
            });
            for(var page in pagetoload){
                this.loadBagPageFromServer(page,true,data);
            }
            this.gridBroadcast(function(grid){
                grid.selection.select(resultattr.prevSelectedIdx);
                grid.scrollToRow(resultattr.prevSelectedIdx);
            });
        }
        return result;
    },
    
    onExternalChangeResult:function(changelist){
        if(changelist.length>0){
            var that = this;
            this.externalChangedKeys = this.externalChangedKeys || {};
            dojo.forEach(changelist,function(n){
                if(n._isExternal){
                    that.externalChangedKeys[n.pkey] = true;
                }
            });
            var prevSelected = {};
            dojo.forEach(this.linkedGrids(),function(grid){
                dojo.forEach(grid.selection.getSelected(), function(idx) {
                    prevSelected[grid.rowIdByIndex(idx)] = true;
                });
                grid._saved_selections = grid.selectionKeeper('save');
            });
            this.storeNode.setRelativeData('.query.prevSelectedDict',prevSelected);
            var that = this;
            var cb = function(result){
                dojo.forEach(that.linkedGrids(),function(grid){
                    grid.sourceNode.publish('onExternalChanged');
                });
                return result;
            };
            var result = this.loadData();
            if(result instanceof dojo.Deferred){
                result.addCallback(function(r){cb(r)});
            }else{
                result = cb(result);
            }
        }
    },
    
    onExternalChange:function(changelist){
        var parentNodeData = this.getData().getParentNode();
        if(!parentNodeData){
            return;
        }
        var selectionKw = parentNodeData.attr;
        if(!selectionKw.selectionName){
            return;
        }
        var that = this;
        var rpc_attr = objectUpdate({},this.storeNode.attr);
        objectExtract(rpc_attr,'_*');
        objectUpdate(rpc_attr,{'selectionName':selectionKw.selectionName,
                                'changelist':changelist,'_sourceNode':this.storeNode});
        genro.rpc.remoteCall('app.checkFreezedSelection', 
                                            rpc_attr,null,null,null,
                                         function(result){
                                            if(result){
                                                that.onExternalChangeResult(changelist);
                                            }
                                            return result;
                                          });
    },

    currentPkeys:function(caption_field){
        var parentNodeData = this.getData().getParentNode();
        if(!parentNodeData){
            return [];
        }
        var selectionKw = parentNodeData.attr;
        if(!selectionKw.selectionName){
            return [];
        }
        var kw = {'table':selectionKw.table,selectionName:selectionKw.selectionName,caption_field:caption_field}


        return genro.rpc.remoteCall('app.freezedSelectionPkeys', 
                                            kw,null,null,null,
                                         function(result){
                                             return result || [];
                                          });
    },
    
    clearBagCache:function() {
        var data = this.getData();
        if(data){
            data.clear();
        }
        this.currRenderedRowIndex = null;
        this.currRenderedRow = null;
        this.currCachedPageIdx = null;
        this.currCachedPage = null;
    },

    itemByIdx:function(idx,sync) {
        var delta = idx-this.lastIdx;
        this.lastIdx = idx;
        var dataPage;
        var rowIdx = idx % this.chunkSize;
        var pageIdx = (idx - rowIdx) / this.chunkSize;
        if (this.currCachedPageIdx != pageIdx) {
            if(!sync){
                dataPage=this.getDataChunk(pageIdx);
            }else{
                dataPage=this.getData().getItem('P_' + pageIdx);
                if (!dataPage){
                    dataPage = this.loadBagPageFromServer(pageIdx,sync);
                }
            }
            
            if (dataPage){
                this.currCachedPageIdx = pageIdx;
                this.currCachedPage=dataPage;
            }else{
                this.currCachedPageIdx=-1;
                this.currCachedPage=null;
            }
        }else{
            if(((delta>0) && ((rowIdx/this.chunkSize)>.7 )) || ((delta<0) && ((rowIdx/this.chunkSize)<.3 ))){
                var guessPage = delta>0?pageIdx+1:pageIdx-1;
                if(guessPage>0){
                    if(guessPage!=this.guessPage){
                        this.getDataChunk(guessPage);
                        this.guessPage = guessPage;
                    }
                }
            }
        }
        if(this.currCachedPage){
            return this.currCachedPage.getNodes()[rowIdx];
        }            
    },

    setExternalChangeClasses:function(item){
        var externalChangedKeys = this.externalChangedKeys || {};
        var row = item.attr;
        var pkey = row['_pkey'];
        if(pkey in externalChangedKeys){
            row['_customClasses'] = row._customClasses? row._customClasses+' externalChangedRow':'externalChangedRow';
            row['_externalChangedRowTS'] = new Date();
            objectPop(externalChangedKeys,pkey);
        }else if(row['_customClasses'] && row['_externalChangedRowTS'] && (new Date()-row['_externalChangedRowTS']>1000)){
            delete row['_externalChangedRowTS'];
            row['_customClasses'] = row['_customClasses'].replace('externalChangedRow','');
        }
    },

    getDataChunk:function(pageIdx){
        if (pageIdx in this.pendingPages){
            return;
        }else{
            var pageData=this.getData().getItem('P_' + pageIdx);
            if (pageData){
                return pageData;    
            }
            if(this.isScrolling && this.storeNode.attr.httpMethod!='WSK'){
                return;
            }
            if(this.pendingTimeout){
                if (this.pendingTimeout.idx==pageIdx){
                    return;
                }else{
                    clearTimeout(this.pendingTimeout.handler);
                    this.pendingTimeout = {};
                }
            }
            var that = this;
            this.pendingTimeout={'idx':pageIdx,
                                'handler':setTimeout(function(){
                                that.loadBagPageFromServer(pageIdx);
                                },10)
            };
            return;
        }
    },

    onChunkLoaded:function(result,pageIdx){
        var data = result.getValue();
        this.getData().setItem('P_' + pageIdx, data,{pageIdx:pageIdx},{'doTrigger':false});
        objectPop(this.pendingPages,pageIdx);
        this.storeNode.publish('updateRows');
        this.pendingTimeout = {};
       //if (this.pendingUpdateGrid){
       //    clearTimeout(this.pendingUpdateGrid);
       //}
       //var that = this;
       //this.pendingUpdateGrid=setTimeout(function(){
       //    that.storeNode.publish('updateRows');
       //},10);
        return data;
    },

    loadBagPageFromServer:function(pageIdx,sync,buffer) {
        var that = this;
        var row_start = pageIdx * this.chunkSize;
        var kw = this.getData().getParentNode().attr;
        var result = genro.rpc.remoteCall(kw.method, {'selectionName':kw.selectionName,
            'row_start':row_start,
            'row_count':this.chunkSize,
            'sortedBy':this.sortedBy,
            'table':kw.table,
            'recordResolver':false},
            null,
            this.storeNode.attr.httpMethod,
            null,
            sync?null:function(result){return that.onChunkLoaded(result,pageIdx);});
        if(sync){
            if(buffer){
                buffer.setItem('P_' + pageIdx, result.getValue(),{pageIdx:pageIdx});
            }else{
                return this.onChunkLoaded(result,pageIdx);
            }
        }else{
            this.pendingPages[pageIdx] = result;
        }
    },
     
    getIdxFromPkey:function(pkey){
        var result = -1;
        var dataNode = this.getData().getNodeByAttr(this.identifier,pkey);
        if(dataNode){
            result = dataNode.attr.rowidx;
        }
        return result;
    },


    getKeyFromIdx:function(idx){
        var dataNode = this.itemByIdx(idx,true);
        return dataNode?this.keyGetter(dataNode):null;
    },

    indexByCb:function(cb,backward){
        var n = this.len(true);
        var pages = this.getData().getNodes();
        var n_pages = pages.length;
        for (var p = 0; p<n_pages; p++){
            var k_p = backward?n_pages-p:p;
            var page = pages[k_p].getValue();
            var rowNodes = page.getNodes();
            var n = rowNodes.length;
            for(var i = 0; i< n; i++){
                var k_i = backward?n-i:i;
                if(cb(this.rowFromItem(rowNodes[i]))){
                    return parseInt(pages[k_p].label.slice(2))*this.chunkSize+k_i;
                }
            }
        }
        return -1;
    },

    filteredRowsIndex:function(){
        console.error('filteredRowsIndex not implemented in virtualstore');
        return [];
    },
    
    sum:function(field){
        var storeattr = this.getData().getParentNode().attr;
        if('sum_'+field in storeattr){
            return storeattr['sum_'+field];
        }else{
            var sum_columns = this.getSumColumns();
            sum_columns = sum_columns?sum_columns.split(','): [];
            arrayPushNoDup(sum_columns,field);
            this.storeNode.setRelativeData('.sum_columns',sum_columns.join(','));
            var rpc_attr = {'selectionName':this.selectionName,sum_column:field};
            rpc_attr.sum_column = field; 
            storeattr['sum_'+field] = genro.rpc.remoteCall('app.sumOnFreezedSelection', 
                                                rpc_attr,
                                                null,null,null,
                                            function(result){
                                                storeattr['sum_'+field] = result;
                                            });
            return storeattr['sum_'+field];
        }
    }
    
});




