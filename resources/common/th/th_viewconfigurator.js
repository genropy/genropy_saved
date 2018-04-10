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
                            {'objtype':'view','metadata':metadata,'data':gridSourceNode.widget.structBag,
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
                        fieldcellattr = fieldcellattr.asDict();
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
        viewAttr['id'] = viewAttr['pkey']
        gridSourceNode.setRelativeData('.currViewAttrs',new gnr.GnrBag(viewAttr));
        this.checkFavorite(gridId);
        if(viewAttr.pkey){
            var pkey = viewAttr.pkey;
            genro.serverCall('_table.adm.userobject.loadUserObject', {pkey:pkey}, function(result){finalize(result.getValue())});
        }else{
            finalize(gridSourceNode.getRelativeData('.resource_structs.'+currPath).deepCopy())
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

    configuratorPalette:function(gridId){
        var gridNode = genro.nodeById(gridId) || genro.nodeBySourceNodeId(gridId);
        var groupCode = '_currentPaletteGridConfigurator_'+gridId;
        var root = genro.src.newRoot();
        genro.src.getNode()._('div', groupCode);
        var node = genro.src.getNode(groupCode).clearValue();
        node.freeze();
        var paletteGroup = node._('PaletteGroup',{title:'Grid configurator '+gridId,
                                                groupCode:groupCode,
                                                height:'400px',width:'600px','dockTo':false});
                                      
        this._gridConfiguratorPalette(paletteGroup,gridNode,groupCode);

        this._selectedColumnConfiguratorPalette(paletteGroup,gridNode,groupCode);

        this._structureConfiguratorPalette(paletteGroup,gridNode,groupCode);

        node.unfreeze();
    },

    _gridConfiguratorPalette:function(parent,gridNode,groupCode){
        var kw = {title:_T('Grid editor'),paletteCode:groupCode+'_grid_overall'};        
        var pane = parent._('PalettePane',kw);
        var tc = pane._('tabContainer',{margin:'2px'});
        var colsetpane = tc._('contentPane',{title:'Columnsets'});
        var structpath = gridNode.absDatapath(gridNode.attr.structpath);

        var grid_pars = {value:'^.columnsets_edit'};
        grid_pars.selfsubscribe_addrow = function(addkw){
            var rowDefaults = objectUpdate({},addkw._askResult);
            rowDefaults['code'] = objectPop(rowDefaults,'columnset');
            this.widget.storebag().setItem(rowDefaults['code'],new gnr.GnrBag(rowDefaults));
        }
        var grid = colsetpane._('quickGrid',grid_pars);
        grid._('column',{name:_T('Code'),field:'code',width:'5em'});
        grid._('column',{name:_T('Name'),field:'name',edit:true,width:'12em'});
        grid._('column',{name:_T('Styles'),field:'styles_columnset',width:'15em',
            _customGetter:function(row){
                return row.styles_columnset?row.styles_columnset.getFormattedValue():'-';
            },
            edit:{modal:true,contentCb:function(pane,kw){
                genro.dom.styleFields(pane._('div',{datapath:'.styles_columnset'}),{blacklist:['height','width']});
            }}});
        grid._('column',{name:_T('Cell styles'),width:'15em',field:'styles_cells',
                _customGetter:function(row){
                return row.styles_cells?row.styles_cells.getFormattedValue():'-';
            },
            edit:{modal:true,contentCb:function(pane,kw){
                    genro.dom.styleFields(pane._('div',{datapath:'.styles_cells'}),{blacklist:['height','border']});
                }}}); 

 
        var t = grid._('tools',{tools:'delrow,addrow',title:_T('Columnsets'),
        custom_tools:{addrow:{content_class:'iconbox add_row',ask:{title:_T('New columnset'),
              fields:[{name:'columnset',lbl:'Code',validate_notnull:true},
                      {name:'name',lbl:'Name'},
                  ]
              }}}});
 
        var dc = pane._('dataController',{script:'this._columnsetsEditor(editbag,destbag,_triggerpars)',
                                            editbag:'^.columnsets_edit',
                                            destbag:'^'+structpath+'.info.columnsets'})
        dc.getParentNode()._columnsetsEditor = function(editbag,destbag,_triggerpars){
            if(_triggerpars.kw.reason=='_columnsetsEditor'){
                return
            }
            if(_triggerpars.kw.pathlist.indexOf('columnsets_edit')>=0){
                if(destbag && destbag.len() && _triggerpars.kw.reason=='loadData'){
                    destbag.forEach(function(n){
                        var r = new gnr.GnrBag(n.attr);
                        editbag.setItem(n.label,r,{_pkey:n.label},{doTrigger:'_columnsetsEditor'});
                    });
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
                        ds.setItem(_triggerpars.kw.node.label,null,_triggerpars.kw.node.getValue().asDict(),{doTrigger:'_columnsetsEditor'});
                        if(!destbag){
                            genro.setData(structpath+'.info.columnsets',ds,null,{doTrigger:'_columnsetsEditor'});
                        }

                    }else{
                        destbag.popNode(_triggerpars.kw.node.label,'_columnsetsEditor');
                    }
                }
            }else{
                //todo
            }
        }
        

    },

    _selectedColumnConfiguratorPalette:function(parent,gridNode,groupCode){
        var gridId = (gridNode.attr.nodeId || gridNode.getStringId());
        var kw = {title:'Column editor',paletteCode:groupCode+'_column_detail'};
        var grid = gridNode.widget;
        var stack_kw = {};
        stack_kw['subscribe_'+gridId+'_onCellClick'] = function(click_kw){
            var colspath = grid.sourceNode.absDatapath(grid.sourceNode.attr.structpath+'.#0.#0');
            var cell = grid.getCell(click_kw.cellNode.cellIndex);
            var cellData = new gnr.GnrBag(genro.getDataNode(colspath+'.'+cell._nodelabel).attr);
            this.setRelativeData('.record',cellData);
            cellData.subscribe('rowLogger',{'upd':function(triggerkw){
                var node = genro.getDataNode(colspath+'.'+cell._nodelabel);
                var updkw = {};
                updkw[triggerkw.node.label] = triggerkw.value;
                node.updAttributes(updkw);
            }});
            this.widget.switchPage(1);
        };
        var pane = parent._('PalettePane',kw);
        var sc = pane._('stackContainer',stack_kw);
        sc._('contentPane')._('div',{innerHTML:'No cell selected'})
        var bc = sc._('borderContainer',{datapath:'.record'});
        var fb;

        fb = genro.dev.formbuilder(bc._('ContentPane',{region:'top'}),1,{border_spacing:'1px',margin:'5px'});
        fb.addField('textbox',{value:'^.name',width:'15em',lbl:'Title'});


        var tc = bc._('TabContainer',{margin:'2px',region:'center'});

        fb = genro.dev.formbuilder(tc._('ContentPane',{title:'Main'}),1,{border_spacing:'1px',margin:'5px'});
        fb.addField('combobox',{value:'^.format',width:'15em',lbl:'Format',values:'short,long,full'});
        fb.addField('textbox',{value:'^.columnset',width:'15em',lbl:'Columnset'});

        if(grid.collectionStore().storeNode.attr.groupByStore){
            fb.addField('combobox',{value:'^.group_aggr',width:'15em',
                        hidden:'^.dtype?="NLIRF".indexOf(#v)<0',
                        lbl:'Aggregator',values:'sum,avg,min,max'}); 
            fb.addField('checkbox',{value:'^.group_nobreak',
                                    hidden:'^.dtype?="NLIRF".indexOf(#v)>=0',
                                    label_hidden :'^.dtype?="NLIRF".indexOf(#v)>=0',
                                    label:_T('Group no break')})
            fb.addField('combobox',{value:'^.group_aggr',values:'MM,YYYY,YYYY-MM,Day',
                                    hidden:'^.dtype?="DDH".indexOf(#v)<0',
                                    lbl:_T('Date as')})
        }

        fb = genro.dev.formbuilder(tc._('ContentPane',{title:'Style'}),1,{border_spacing:'1px',margin:'5px'});
        fb.addField('colorTextBox',{value:'^.background',width:'15em',lbl:'Background',mode:'rgba'});
        fb.addField('colorTextBox',{value:'^.color',width:'15em',lbl:'Foreground'});
        fb.addField('textbox',{value:'^.width',width:'15em',lbl:'Width'});

        //fb = genro.dev.formbuilder(tc._('ContentPane',{title:'Ranges'}),3,{border_spacing:'1px'});


    },

    _structureConfiguratorPalette:function(parent,gridNode,groupCode){
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
        var kw = {title: _T('Advanced configuration'),
        'paletteCode':groupCode+'_struct_editor',
        addrow:addrow,delrow:true,
        grid_nodeId:(gridNode.attr.nodeId || gridNode._id)+'_viewEditor',
        grid_addCheckBoxColumn:{field:'hidden',trueclass:'checkboxOff',falseclass:'checkboxOn'},
        grid_onCreated:function(widget){
            dojo.connect(grid,'onSetStructpath',function(){
                widget.updateRowCount();
            });
        },
        'path':colspath,
        exclude:'dtype,field,tag,related_table,related_table_lookup,related_column,relating_column,rowcaption,caption_field'};
        parent._('PaletteBagEditor',kw);
    }

};
    
    
    