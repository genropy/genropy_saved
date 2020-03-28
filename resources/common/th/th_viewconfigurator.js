var genro_plugin_grid_configurator = {
    deleteGridView:function(gridId) {
        var gridSourceNode = genro.nodeById(gridId);
        var that = this;
        var currViewAttr = gridSourceNode.getRelativeData('.currViewAttrs');
        genro.serverCall('_table.adm.userobject.deleteUserObject', {pkey:currViewAttr.getItem('pkey')}, function() {
            genro.grid_configurator.loadView(gridId);
            that.refreshMenu(gridId);
        });
    },

    setCurrentAsDefault:function(gridId){
        var gridSourceNode = genro.nodeById(gridId);
        genro.setInStorage("local", this.storeKey(gridId), gridSourceNode.getRelativeData('.currViewPath'));
        this.checkFavorite(gridId);
    },
    storeKey:function(gridId){
        return 'view_' + genro.getData('gnr.pagename') + '_' + gridId +'_struct';
    },
    setFavoriteView:function(gridId){
        var gridSourceNode = genro.nodeById(gridId);
        var favoritePath = genro.getFromStorage("local", this.storeKey(gridId)) || '__baseview__';        
        gridSourceNode.setRelativeData('.favoriteViewPath',favoritePath);
        //this.setCurrentAsDefault(gridId);
    },
    
    saveGridView:function(gridId) {
        var gridSourceNode = genro.nodeById(gridId);
        var selectedViewCode = gridSourceNode.getRelativeData('.currViewAttrs.code');
        var datapath =  gridSourceNode.absDatapath('.currViewAttrs');
        var objtype = 'view';
        var collectionStore = gridSourceNode.widget.collectionStore();
        if(collectionStore.storeNode.attr.groupByStore){
            objtype = 'grpview';
        }
        var that = this;
        saveCb = function(dlg) {
            var pagename = genro.getData('gnr.pagename');
            var flag =  pagename+'_'+gridId;
            var metadata = genro.getData(datapath);
            var flags = metadata.getItem('flags');
            if(flags){
                if(flags.indexOf(flag)<0){
                    flags = flags.split(',');
                    flags.push(flag);
                }
            }else{
                flags = flag;
            }

            metadata.setItem('flags',flags);
            genro.serverCall('_table.adm.userobject.saveUserObject',
                            {'objtype':objtype,'metadata':metadata,'data':gridSourceNode.widget.structBag,
                            table:gridSourceNode.attr.table},
                            function(result) {
                                dlg.close_action();
                                gridSourceNode.setRelativeData('.currViewPath', result.attr.code);
                                that.refreshMenu(gridId);
                            });
        };
        genro.dev.userObjectDialog(selectedViewCode ? 'Save View ' + selectedViewCode : 'Save New View',datapath,saveCb);
    },
    

    addGridConfigurator:function(sourceNode){
        sourceNode.attr.selfDragColumns = 'trashable';
        var table = sourceNode.attr.table;
        if(!table && sourceNode.attr.storepath){
            table = genro.getDataNode(sourceNode.widget.absStorepath()).attr.dbtable;
            sourceNode.attr.table = table; 
        }
        if(table){
            var tablecode = table.replace('.', '_');
            var fieldcellattr;
            sourceNode.attr['onDrop_gnrdbfld_' + tablecode] = function(dropInfo, data) {
                var grid = this.widget;
                if(dropInfo.event.shiftKey){
                    fieldcellattr = genro.serverCall('app.getFieldcellPars',{field:data.fieldpath,table:data.maintable});
                    if(fieldcellattr){
                        fieldcellattr = fieldcellattr.asDict(null,true);
                    }
                }
                if(sourceNode.attr.onDroppedColumn){
                    var treeNode = genro.src.nodeBySourceNodeId(dropInfo.dragSourceInfo._id);
                    funcApply(sourceNode.attr.onDroppedColumn,{data:data, column:dropInfo.column,fieldcellattr:fieldcellattr,treeNode:treeNode},grid);
                }else{
                    grid.addColumn(data, dropInfo.column,fieldcellattr);
                }
                
            };
            sourceNode.attr.dropTarget_column = sourceNode.attr.dropTarget_column ? sourceNode.attr.dropTarget_column + ',' + 'gnrdbfld_' + tablecode : 'gnrdbfld_' + tablecode;
            sourceNode.dropModes.column = sourceNode.attr.dropTarget_column;
        }
        sourceNode._gridConfiguratorBuilt=true;
    },
    
    loadView:function(gridId,currPath){
        var gridSourceNode = genro.nodeById(gridId);
        currPath = currPath || gridSourceNode.getRelativeData('.favoriteViewPath') || '__baseview__';
        var resource_structs = gridSourceNode.getRelativeData('.resource_structs');
        var structbag,structnode,viewAttr;
        var finalize = function(struct){
             gridSourceNode.setRelativeData(gridSourceNode.attr.structpath,struct);
             //if(gridSourceNode.widget && gridSourceNode.widget.storeRowCount()>0){
             //    gridSourceNode.widget.reload(true);
             //}
        }
        
        if(resource_structs){
            structnode = resource_structs.getNode(currPath);
            if(structnode){
                viewAttr = structnode.attr;
                structbag = structnode._value;
            }
        }
        if(!structbag){
            var menubag = gridSourceNode.getRelativeData('.structMenuBag');
            if(!menubag.getNode(currPath)){
                gridSourceNode.setRelativeData('.currViewPath','__baseview__');
                return;
            }
            viewAttr = menubag.getNode(currPath).attr;
        }        
        viewAttr.id = viewAttr.pkey;
        gridSourceNode.setRelativeData('.currViewAttrs',new gnr.GnrBag(viewAttr));
        this.checkFavorite(gridId);
        if(viewAttr.pkey){
            var pkey = viewAttr.pkey;
            genro.serverCall('_table.adm.userobject.loadUserObject', {pkey:pkey}, function(result){finalize(result.getValue());});
        }else{
            finalize(gridSourceNode.getRelativeData('.resource_structs.'+currPath).deepCopy());
        }
    },
    refreshMenu:function(gridId){
        var gridSourceNode = genro.nodeById(gridId);
        var menubag = gridSourceNode.getRelativeData('.structMenuBag');
        if(!menubag){
            return;
        }
        menubag.getParentNode().getResolver().reset();
    },
    checkFavorite:function(gridId){
        var frame = genro.getFrameNode(gridId.replace('_grid',''));
        var gridSourceNode = genro.nodeById(gridId);
        if(!frame){
            return;
        }
        var currPath = gridSourceNode.getRelativeData('.currViewPath');
        var currfavorite = genro.getFromStorage("local", this.storeKey(gridId));
        gridSourceNode.setRelativeData('.favoriteViewPath',currfavorite);
        //this.refreshMenu(gridId);
        genro.dom.setClass(frame,'th_isFavoriteView',currfavorite==currPath);
    },

    _colParametersFields:function(){
       var fields = [
            {'field':'name','dtype':'T','widget':{'tag':'Textbox','width':'15em','lbl':_T('Name')}},
            {'field':'columnset','dtype':'T','widget':{'tag':'ComboBox','width':'15em','lbl':_T('Columnset')}}, //to complete
            {'field':'formula','dtype':'T','widget':{'tag':'Textbox','lbl':_T('Formula'),'width':'15em','hidden':'^.?calculated?=!#v'}},//to complete
            {'field':'hidden','dtype':'B','widget':{'tag':'checkbox','label':_T('Hidden'),'hidden':'^.?dtype?="NRFLI".indexOf(#v)<0'}},
            {'field':'totalize','dtype':'B','widget':{'tag':'checkbox','label':_T('Totalize'),'hidden':'^.?dtype?="NRFLI".indexOf(#v)<0'}},
            {'field':'subtotal','dtype':'B','widget':{'tag':'checkbox','label':_T('Subtotal'),'hidden':'^.?dtype?="NRFLI".indexOf(#v)>=0'}},
        ];
        return fields;

    },
    configuratorColsetTooltip:function(gridId,colset,event){
        if(!colset){
            return;
        }
        var gridNode = genro.nodeById(gridId) || genro.nodeBySourceNodeId(gridId);
        var structpath = gridNode.absDatapath(gridNode.attr.structpath);
        genro.dlg.quickTooltipPane({modal:true,domNode:event.target},
            function(tp,kw){
                var pane = tp._('div',{datapath:`${structpath}.info.columnsets.${colset.code}`,font_size:'.9em'});
                var topbar = pane._('div',{_class:'commonTitleBar',innerHTML:`Edit columnset ${colset.code}`});
                var box = pane._('div',{padding:'10px'});
                var fb = genro.dev.formbuilder(box,1,{border_spacing:'3px',lbl_color:'#666',label_color:'#666'});
                fb.addField('textbox',{value:'^.?name',lbl:'Name'});
                genro.dom.styleFields(fb,{parentFb:true,prefix:'?',blacklist:['height','width']});
                fb.addField('div',{'innerHTML':_T('Cell Styles'),font_weight:'bold'});
                genro.dom.styleFields(fb,{parentFb:true,prefix:'?cells_',blacklist:['height','width']});

            });
    },

    configuratorCellTooltip:function(gridId,cell,parentDomNode){
        if(!cell){
            return;
        }
        var fields = this._colParametersFields();
        var gridNode = genro.nodeById(gridId) || genro.nodeBySourceNodeId(gridId);
        var grid = gridNode.widget;
        var structpath = gridNode.absDatapath(gridNode.attr.structpath);
        var that = this;
        genro.dlg.quickTooltipPane({modal:true,domNode:parentDomNode},
            function(tp,tpkw){
                var pane = tp._('div',{datapath:`${structpath}.view_0.rows_0.${cell._nodelabel}`,font_size:'.9em'});
                var topbar = pane._('div',{_class:'commonTitleBar',innerHTML:`Edit cell ${cell.field}`});
                topbar._('menu',{'_class':'smallMenu','modifiers':'*','storepath':`#${gridId}.menuColsConfigMenu`,
                                    action:function(kw){
                                        genro.nodeById(tpkw.tooltipOpenerId).publish('close');
                                        if(kw.cell=='newcell'){
                                            genro.dlg.prompt(_T('Add col'),{'widget':[{lbl:'name',value:'^.field'},
                                             {lbl:'dtype',value:'^.dtype',wdg:'filteringSelect',values:'T:Text,N:Number,B:Boolean'},
                                             {lbl:'formula',value:'^.formula'}
                                            ],
                                                action:function(result){
                                                            var b = genro.getData(structpath);
                                                            var kw = result.asDict();
                                                            kw.name = kw.field;
                                                            kw.calculated= true; 
                                                            b.setItem('#0.#0.cell_'+genro.getCounter(),null,kw);
                                                            //that.configuratorCellTooltip(gridId,grid.cellmap[field],parentDomNode);
                                                        }
                                                });
                                        }else{
                                            that.configuratorCellTooltip(gridId,kw.cell,parentDomNode);
                                        }
                                    },
                                });
                var box = pane._('div',{padding:'10px'});
                var fb = genro.dev.formbuilder(box,1,{border_spacing:'3px',lbl_color:'#666',label_color:'#666'});
                //fb.addField('textbox',{value:'^.?name',lbl:'Name'});
                fields.forEach(function(fieldkw){
                    var wdgkw = objectUpdate({},fieldkw.widget); 
                    wdgkw.value = `^.?${fieldkw.field}`;
                    if(fieldkw.field=='columnset'){
                        wdgkw.values = `=${structpath}.info.columnsets?=#v?#v.keys().join(","):null`;
                        wdgkw.validate_onAccept = function(value){
                            if(value){
                                var currColset = this.getRelativeData(`${structpath}.info.columnsets`) || new gnr.GnrBag();
                                if(currColset.index(value)<0){
                                    currColset.addItem(value.toLowerCase(),null,{code:value.toLowerCase(),name:stringCapitalize(value)});
                                }
                                this.setRelativeData(`${structpath}.info.columnsets`,currColset);
                            }
                        };
                    }
                    fb.addField(objectPop(wdgkw,'tag'),wdgkw);
                });
                fb.addField('textbox',{value:'^.?format',lbl:'Format'});
                fb.addField('filteringSelect',{value:'^.?sort',lbl:'Sort',values:'a:Asc,d:Desc'});
                fb.addField('div',{'innerHTML':'&nbsp;',font_weight:'bold',border_top:'1px solid silver'});
                genro.dom.styleFields(fb,{parentFb:true,prefix:'?',blacklist:['height','width']});
            });
    },


    configuratorPalette:function(gridId){
        var gridNode = genro.nodeById(gridId) || genro.nodeBySourceNodeId(gridId);
        var paletteCode = '_currentPaletteGridConfigurator_'+gridId;
        var paletteWdg = genro.wdgById(paletteCode+'_floating');
        if(paletteWdg){
            paletteWdg.show();
            return;
        }
        var root = genro.src.newRoot();
        genro.src.getNode()._('div', paletteCode);
        var node = genro.src.getNode(paletteCode).clearValue();
        node.freeze();
        var title = gridNode.attr.item_name_plural?' '+gridNode.attr.item_name_plural:'';
        var pane = node._('PalettePane',{title:'Grid configurator'+title,
                                                paletteCode:paletteCode,
                                                height:'500px',width:'800px','dockTo':'dummyDock:open'});

        var frame = pane._('framePane',{frameCode:paletteCode+'_panels',center_widget:'stackContainer'});
        var bar = frame._('slotBar',{slots:'2,stackButtons,*,saveConfiguration,2',toolbar:true,side:'top'});
        var that = this;
        if(!gridNode.attr.externalSave){
            bar._('slotButton','saveConfiguration',{iconClass:'iconbox save',
                action:function(){
                    that.saveGridView(gridId);
                }});
        }
        this._cellsEditorGrid(frame,gridNode);
        this._columnsetsGrid(frame,gridNode);
        this._structureConfigurator(frame,gridNode);
        node.unfreeze();
    },

    _columnsetsGrid:function(tc,gridNode){
        var pane = tc._('contentPane',{title:'Columnsets',datapath:'.colseteditor',margin:'2px'});
        var structpath = gridNode.absDatapath(gridNode.attr.structpath);
        var grid_pars = {value:'^.columnsets_edit',nodeId:(gridNode.attr.nodeId || gridNode._id)+'_columnsetsGrid'};
        grid_pars.selfsubscribe_addrow = function(addkw){
            var rowDefaults = objectUpdate({},addkw._askResult);
            rowDefaults.code = objectPop(rowDefaults,'columnset');
            this.widget.storebag().setItem(rowDefaults.code,new gnr.GnrBag(rowDefaults));
        }
        var grid = pane._('quickGrid',grid_pars);
        grid._('column',{name:_T('Code'),field:'code',width:'5em'});
        grid._('column',{name:_T('Name'),field:'name',edit:true,width:'12em'});
        this._subBagCell(grid,'styles_columnset','Styles',genro.dom.styleFields,{blacklist:['height','width']});
        this._subBagCell(grid,'styles_cells','Cell styles',genro.dom.styleFields,{blacklist:['height','border']});
 
        var t = grid._('tools',{tools:'delrow,addrow',title:_T('Columnsets'),
        custom_tools:{addrow:{content_class:'iconbox add_row',ask:{title:_T('New columnset'),
              fields:[{name:'columnset',lbl:'Code',validate_notnull:true},
                      {name:'name',lbl:'Name'},
                  ]
              }}}});
        var dc = pane._('dataController',{script:'this._columnsetsEditor(editbag,destbag,_triggerpars)',
                                            editbag:'^.columnsets_edit',
                                            destbag:'^'+structpath+'.info.columnsets'});
        dc.getParentNode()._columnsetsEditor = function(editbag,destbag,_triggerpars){
            var rebuildEditBag = function(editbag){
                var destbag = genro.getData(structpath+'.info.columnsets');
                editbag.getNodes().forEach(function(n){
                    editbag.popNode(n.label,'_columnsetsEditor');
                });
                if(!destbag){
                    destbag = new gnr.GnrBag();
                    genro.setData(structpath+'.info.columnsets',destbag);
                    return;
                }
                destbag.forEach(function(n){
                    var r = objectUpdate({},n.attr);
                    var currStyles = objectExtract(r,genro.dom.editableStyles.join(','));
                    var currCellStyles = objectExtract(objectExtract(r,'cells_*'),genro.dom.editableStyles.join(','));
                    r = new gnr.GnrBag(r);
                    r.setItem('styles_columnset',new gnr.GnrBag(currStyles));
                    r.setItem('styles_cells',new gnr.GnrBag(currCellStyles));
                    editbag.setItem(n.label,r,{_pkey:n.label},{doTrigger:'_columnsetsEditor'});
                });
            };
            if(_triggerpars.kw.reason=='_columnsetsEditor'){
                return;
            }
            if(_triggerpars.kw.pathlist.indexOf('columnsets_edit')>=0){
                if(destbag && destbag.len() && _triggerpars.kw.reason=='loadData'){
                    rebuildEditBag(editbag);
                }else if(_triggerpars.trigger_reason=='child'){
                    var evt = _triggerpars.kw.evt;
                    if(evt=='upd'){
                        var rowNode = _triggerpars.kw.node.getParentNode();
                        var updDict = {};
                        var updValue = _triggerpars.kw.node.getValue();
                        if(rowNode.label.startsWith('styles_')){
                            rowNode.getValue().forEach(function(n){
                                var prefix = rowNode.label=='styles_cells'?'cells_':'';
                                if(n.getValue()!==null){
                                    updDict[prefix+n.label] = n.getValue();
                                }
                            });
                            rowNode = rowNode.getParentNode();
                        }else{
                            updDict[_triggerpars.kw.node.label] = updValue;
                        }
                        destbag.getNode(rowNode.label).updAttributes(updDict,'_columnsetsEditor');
                    }else if(evt=='ins'){
                        var ds = destbag || new gnr.GnrBag(); 
                        ds.setItem(_triggerpars.kw.node.label,null,_triggerpars.kw.node.getValue().asDict('flat',true),{doTrigger:'_columnsetsEditor'});
                        if(!destbag){
                            genro.setData(structpath+'.info.columnsets',ds,null,{doTrigger:'_columnsetsEditor'});
                        }
                    }else{
                        destbag.popNode(_triggerpars.kw.node.label,'_columnsetsEditor');
                    }
                }
            }else{
                rebuildEditBag(editbag);
            }
        };
    },


    _cellsEditorGrid:function(tc,gridNode){
        var pane = tc._('contentPane',{title:_T('Columns'),margin:'2px',datapath:'.cellseditor'});
        var structpath = gridNode.absDatapath(gridNode.attr.structpath);

        var grid_pars = {value:'^.cells_edit',nodeId:(gridNode.attr.nodeId || gridNode._id)+'_cellsEditorGrid'};
        grid_pars.selfDragRows = true;
        grid_pars.selfsubscribe_addrow = function(addkw){
            var rowDefaults = objectUpdate({},addkw._askResult);
            rowDefaults.calculated = true;
            this.widget.storebag().setItem('cellx_'+genro.time36Id(),new gnr.GnrBag(rowDefaults));
        };
        var grid = pane._('quickGrid',grid_pars);
        var fldgetter = function(attr){
            attr = attr[0];
            var result = attr.field.replace(/\W/g, '_');
            if(attr.group_aggr){
                result+= '_'+attr.group_aggr.replace(/\W/g, '_').toLowerCase();
            }
            return result;
        };
        var formulaPane = function(pane){
            var fb = genro.dev.formbuilder(pane,1,{border_spacing:'1px',margin:'5px'});
            var values = genro.getData(structpath+'.view_0.rows_0').digest('#a');
            values = values.map(fldgetter).join(',');
            var tb = fb.addField('textbox',{lbl:_T('Formula'),value:'^.formula',width:'40em'});
            tb._('ComboMenu',{values:values,action:function(kw,ctx){
                var cv = this.attr.attachTo.widget.getValue();
                this.attr.attachTo.widget.setValue(cv?cv+' '+kw.fullpath:kw.fullpath);
            }});
        }
        grid._('column',{name:_T('Field'),field:'field',width:'12em'});
        grid._('column',{name:_T('Type'),field:'dtype',width:'5em'});
        grid._('column',{name:_T('Name'),field:'name',edit:true,width:'12em'});
        grid._('column',{name:_T('Formula'),field:'formula',editDisabled:'=#ROW.calculated?=!#v',
                                edit:{modal:true,contentCb:function(pane){formulaPane(pane);}},width:'12em'});
        grid._('column',{name:_T('Columnset'),field:'columnset',edit:{tag:'ComboBox',
                                            values:'='+structpath+'.info.columnsets'+'?=#v?#v.keys().join(","):null'},
                                            width:'8em'});
        grid._('column',{name:'T',field:'totalize',dtype:'B',edit:true,
                        editDisabled:'=#ROW.dtype?="NRFLI".indexOf(#v)<0',width:'4em'});
        grid._('column',{name:_T('Format'),field:'format',edit:true,width:'8em'});
        grid._('column',{name:_T('Sort'),field:'sort',edit:{tag:'filteringSelect',values:'a:Asc,d:Desc'},width:'4em'});

        this._subBagCell(grid,'styles_cells','Cell styles',genro.dom.styleFields,{blacklist:['height','border']});
        if(gridNode.widget.collectionStore().storeNode.attr.groupByStore){
            this._subBagCell(grid,'group_pars','Grouping Pars',function(pane){
                genro.groupth.groupByParsFields(genro.dev.formbuilder(pane,1,{border_spacing:'1px',margin:'5px'}),
                                            pane.getParentNode().getRelativeData('.#parent.dtype'));
            });
        }
        var t = grid._('tools',{tools:'delrow,addrow',title:_T('Cells'),
        custom_tools:{addrow:{content_class:'iconbox add_row',ask:{title:_T('New formula cell'),
              fields:[{name:'field',lbl:'Field',validate_notnull:true},
                      {name:'name',lbl:'Name'},
                      {name:'dtype',lbl:'Type',wdg:'filteringSelect',values:'N:Decimal,L:Integer,T:Text,B:Boolean,D:Date'}
                  ]
              }}}});
        var dc = pane._('dataController',{script:'this._cellsEditor(editbag,destbag,_triggerpars)',
                                            editbag:'^.cells_edit',
                                            destbag:'^'+structpath+'.view_0.rows_0'});
        var that = this;
        dc.getParentNode()._cellsEditor = function(editbag,destbag,_triggerpars){
            that._cellsEditorConverter(editbag,destbag,_triggerpars,'.view_0.rows_0','cellsEditor');
        };
    },

    _structureConfigurator:function(tc,gridNode){
        var colspath = gridNode.absDatapath(gridNode.attr.structpath+'.#0.#0');
        var grid = gridNode.widget;
        var addrow = {content_class:'iconbox add_row',dtype:'N',calculated:true,
                        ask:{title:_T('New Column'),
                            fields:[{name:'field',lbl:'Field',validate_notnull:true},
                                    {name:'name',lbl:'Name'},
                                    {name:'dtype',lbl:'Dtype',values:'N:Numeric,T:Text,D:Date',wdg:'Combobox'},
                                    {name:'formula',lbl:'Formula'},
                                    {name:'calculated',label:'Calculated',wdg:'checkbox'}]}
        };
        var kw = {addrow:addrow,delrow:true,
            grid_nodeId:(gridNode.attr.nodeId || gridNode._id)+'_advancedEditor',
            grid_addCheckBoxColumn:{field:'hidden',trueclass:'checkboxOff',falseclass:'checkboxOn'},
            grid_onCreated:function(widget){
                dojo.connect(grid,'onSetStructpath',function(){
                    widget.updateRowCount();
                });
            },'path':colspath,
            exclude:'dtype,field,tag,related_table,related_table_lookup,related_column,relating_column,rowcaption,caption_field'};
        tc._('contentPane',{title:_T('Advanced configuration'),overflow:'hidden',datapath:'.advanced'})._('FlatBagEditor',kw);
    },


    _subBagCell:function(grid,field,name,cb,cpars){
        grid._('column',{name:_T(name),width:'15em',field:field,
                _customGetter:function(row){return row[field]?row[field].getFormattedValue():'-';},
                edit:{modal:true,contentCb:function(pane,kw){
                    cb(pane._('div',{datapath:'.'+field}),cpars);}}}); 
    },

    _cellsEditorConverter:function(editbag,destbag,_triggerpars,relpath,reason){
        if(_triggerpars.kw.reason==reason){
            return;
        }
        var rebuildEditBag = function(destbag,editbag){
            editbag.clear();
            destbag.forEach(function(n){
                var r = objectUpdate({},n.attr);
                var currStyles = objectExtract(r,genro.dom.editableStyles.join(','));
                var group_pars = objectExtract(r,'group_*',null,true);
                r = new gnr.GnrBag(r);
                r.setItem('styles_cells',new gnr.GnrBag(currStyles));
                r.setItem('group_pars',new gnr.GnrBag(group_pars));
                editbag.setItem(n.label,r,{_pkey:n.label},{doTrigger:reason});
            });
        };
        if(_triggerpars.kw.pathlist.indexOf('cells_edit')>=0){
            if(destbag && destbag.len() && _triggerpars.kw.reason=='loadData'){
                rebuildEditBag(destbag,editbag);
            }else if(_triggerpars.trigger_reason=='child'){
                var evt = _triggerpars.kw.evt;
                if(evt=='upd'){
                    var rowNode = _triggerpars.kw.node.getParentNode();
                    var updDict = {};
                    var updValue = _triggerpars.kw.node.getValue();
                    if(['styles_cells','group_pars'].indexOf(rowNode.label)>=0){
                        rowNode.getValue().forEach(function(n){
                            updDict[n.label] = n.getValue();
                        });
                        if(updDict.group_aggr=='nobreak' || updDict.group_aggr=='break'){
                            if(updDict.group_aggr=='nobreak'){
                                updDict.group_nobreak = true;
                            }
                            updDict.group_aggr = false;
                        }
                        rowNode = rowNode.getParentNode();
                    }else{
                        updDict[_triggerpars.kw.node.label] = updValue;
                    }
                    destbag.getNode(rowNode.label).updAttributes(updDict,reason);
                }else if(evt=='ins'){
                    var ds = destbag || new gnr.GnrBag(); 
                    ds.setItem(_triggerpars.kw.node.label,null,_triggerpars.kw.node.getValue().asDict('flat',true),{doTrigger:reason,
                                                _position:_triggerpars.kw.ind});
                    if(!destbag){
                        genro.setData(structpath+relpath,ds,null,{doTrigger:reason});
                    }
                }else if (evt=='del'){
                    destbag.popNode(_triggerpars.kw.node.label,reason);
                }
            }
        }else{
            rebuildEditBag(destbag,editbag);
        }
    }

};
    
    
    