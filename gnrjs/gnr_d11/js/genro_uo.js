/*
 *-*- coding: UTF-8 -*-
 *--------------------------------------------------------------------------
 * package       : Genro js - see LICENSE for details
 * module genro_dev : Genro clientside developement module
 * Copyright (c) : 2004 - 2007 Softwell sas - Milano
 * Written by    : Giovanni Porcari, Francesco Cavazzana
 *                 Saverio Porcari, Francesco Porcari
 *--------------------------------------------------------------------------
 *This library is free software; you can redistribute it and/or
 *modify it under the terms of the GNU Lesser General Public
 *License as published by the Free Software Foundation; either
 *version 2.1 of the License, or (at your option) any later version.

 *This library is distributed in the hope that it will be useful,
 *but WITHOUT ANY WARRANTY; without even the implied warranty of
 *MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
 *Lesser General Public License for more details.

 *You should have received a copy of the GNU Lesser General Public
 *License along with this library; if not, write to the Free Software
 *Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA
 */



//######################## genro UserObject  #########################

class UserObjectHandler{
    constructor(sourceNode,objtype,table,dataIndex,onSaved,onLoaded){
        this.sourceNode = sourceNode;
        this.objtype = objtype;
        this.table = table;
        this.dataIndex = dataIndex;
    }
    load(){}
    save(){
        var datapath = sourceNode.absDatapath(kw.metadataPath);
        var saveAs = objectPop(kw,'saveAs');
        var currentMetadata = genro.getData(datapath);
        var userObjectIsLoaded = currentMetadata && currentMetadata.getItem('code');
        var preview = objectPop(kw,'preview');
        var saveCb = function(dlg,evt,counter,modifiers){
            var data = new gnr.GnrBag();
            if(kw.dataIndex){
                for(var key in kw.dataIndex){
                    data.setItem(key,sourceNode.getRelativeData(kw.dataIndex[key]));
                }
                data.setItem('__index__',new gnr.GnrBag(kw.dataIndex));
            }else if(kw.dataSetter){
                funcApply(kw.dataSetter,{data:data},sourceNode);
            }
            var metadata = new gnr.GnrBag(kw.defaultMetadata);
            metadata.update(genro.getData(datapath));
            if (!metadata.getItem('code')){
                genro.publish('floating_message',{message:_T('Missing code'),messageType:'error'});
                return;
            }
            return genro.serverCall('_table.adm.userobject.saveUserObject',
                {'objtype':kw.objtype,'table':kw.table,flags:kw.flags,
                'data':data,metadata:metadata},
                function(result) {
                    if(dlg){
                        dlg.close_action();
                    }else{
                        var objname = result.attr.description || result.attr.code;
                        genro.publish('floating_message',{message:_T('Saved object '+objname)});
                    }
                    if(kw.loadPath){
                        sourceNode.setRelativeData(kw.loadPath, result.attr.code);
                    }
                    if(onSaved){
                        funcApply(onSaved,{result:result},sourceNode);
                    }
                    genro.setData(datapath,new gnr.GnrBag(result.attr));
                    return result;
                });
        };
        if(userObjectIsLoaded && !saveAs){
            return saveCb();
        }
        this.dialog();
    }
    dialog(){
        var dlg = genro.dlg.quickDialog(title);
        var center = dlg.center;
        var box = center._('div', {datapath:datapath,padding:'20px'});
        var fb = genro.dev.formbuilder(box, 2, {border_spacing:'6px'});
        fb.addField('textbox', {lbl:_T("Code"),value:'^.code',width:'10em'});
        fb.addField('checkbox', {label:_T("Private"),value:'^.private'});
        fb.addField('textbox', {lbl:_T("Name"),value:'^.description',width:'100%',colspan:2});
        fb.addField('textbox', {lbl:_T("Authorization"),value:'^.authtags',width:'100%',colspan:2});
        fb.addField('simpleTextArea', {lbl:_T("Notes"),value:'^.notes',width:'100%',height:'5ex',colspan:2,lbl_vertical_align:'top'});
        if(preview){
            fb.addField('button',{action:function(){
                var that = this;
                dlg.getParentNode().widget.hide(); 
                genro.dev.takePicture(function(data){
                    dlg.getParentNode().widget.show(); 
                    that.setRelativeData('.preview',data);
                });
            },label:_T('Screenshot')});
            fb.addField('br',{});
            fb.addField('img',{src:'^.preview',height:'50px',width:'200px',boder:'1px solid silver'});
        }
        var bottom = dlg.bottom._('div');
        var saveattr = {'float':'right',label:_T('Save')};        
        saveattr.action = function(evt,counter,modifiers){
            saveCb(dlg,evt,counter,modifiers);
        };
        bottom._('button', saveattr);
    
        var meta = genro.getData(datapath) || new gnr.GnrBag();
        if(meta.getItem('id') || meta.getItem('pkey')){
            var savecopy = {'float':'right',label:_T('Duplicate as')};        
            savecopy.action = function(evt,counter,modifiers){
                genro.getData(datapath).setItem('id',null);
                genro.getData(datapath).setItem('pkey',null);
                saveCb(dlg,evt,counter,modifiers);
            };
            bottom._('button', savecopy);
        }
    
        bottom._('button', {'float':'right',label:_T('Cancel'),action:dlg.close_action});
        dlg.show_action();
    }

}
userObjectSave:function(sourceNode,kw,onSaved){

},

userObjectLoad:function(sourceNode,kw){
    var metadataPath = objectPop(kw,'metadataPath');
    var onLoaded = objectPop(kw,'onLoaded');
    var onLoading = objectPop(kw,'onLoading');
    var resback = function(result){
        var resultValue,resultAttr,dataIndex;
        if(!result){
            resultValue = new gnr.GnrBag(kw.defaultData);
            resultAttr = objectUpdate({},kw.defaultMetadata);
            dataIndex = kw.dataIndex;
        }else{
            resultValue = result._value.deepCopy();
            resultAttr = objectUpdate({},result.attr);
            dataIndex = resultValue.pop('__index__');
        }
        if(onLoading){
            funcApply(onLoading,null,sourceNode,
                    ['dataIndex','resoultValue','resoultAttr'],
                    [dataIndex,resultValue,resultAttr]);
        }
        sourceNode.setRelativeData(metadataPath,new gnr.GnrBag(resultAttr));
        if(dataIndex){
            if(dataIndex instanceof gnr.GnrBag){
                dataIndex = dataIndex.asDict();
            }
            for(let k in dataIndex){
                sourceNode.setRelativeData(dataIndex[k],resultValue.getItem(k));
            }
        }
        if(onLoaded){
            funcApply(onLoaded,null,
                    sourceNode,['dataIndex','resoultValue','resoultAttr'],
                    [dataIndex,resultValue,resultAttr]);
        }
    }; 
    if(kw.userObjectIdOrCode==='__newobj__'){
        return resback();
    }

    genro.serverCall('_table.adm.userobject.loadUserObject',kw,resback);
},


userObjectMenuData:function(kw,extraRows){
    if(extraRows){
        kw._onResult = function(result){
            var offset = result.len();
            if(offset){
                result.setItem('r_'+offset,null,{caption:'-'});
            }
            offset+=1;
            extraRows.forEach(function(n,i){
                result.setItem('r_'+(i+offset),null,n);
            });
        };
    }
    var resolver = genro.rpc.remoteResolver('_table.adm.userobject.userObjectMenu', kw);
    return resolver;
},