var tableModuleEditor = {

    setCurrentStruct:function(sourceNode,checkedCols){
        var struct = new gnr.GnrBag();
        var cells = new gnr.GnrBag();
        struct.setItem('view_0.rows_0',cells);
        checkedCols = checkedCols || 'name';
        var addedCols = [];
        var columnsCellAttr = this.columnsCellAttr();
       
        checkedCols = ['name','tag'].concat(checkedCols.split(','))
        checkedCols.forEach(function(n){
            cells.setItem('cell_'+n,null,objectUpdate({field:n,edit:true,autoWdg:true,name:n,width:'10em'},columnsCellAttr.getAttr(n)));
        });
        sourceNode.setRelativeData('#FORM.moduleColumnsStruct',struct);
    },

    getCheckableCols:function(data){
        var result = [];
        var mandatory = {};
        this.columnsCellAttr().forEach(function(n){
            if(n.getValue()){
                result.push(n.label);
            }else{
                mandatory[n.label] = true;
            }
        });
        if(data){
            var v;
            data.forEach(function(r){
                r.getValue().forEach(function(c){
                    if(c.label in mandatory){
                        return;
                    }
                    if(result.indexOf(c.label)<0){
                        result.push(c.label);
                    }
                })
            });
        }
        return result.join(',');
    },


    columnsCellAttr:function(){
        var result = this._columnsCellAttr;
        if(!result){
            result = new gnr.GnrBag();
            result.setItem('name',false);
            result.setItem('tag',false,{edit:false,hidden:true});
            result.setItem('dtype',true,{'width':'5em','edit':{'tag':'filteringSelect','values':'T:Text,I:Int,N:Decimal,B:Bool,D:Date,DH:Timestamp,X:Bag'}})
            result.setItem('size',true,{'width':'5em'})
            result.setItem('name_long',true)
            result.setItem('name_short',true)
            result.setItem('group',true,{'width':'5em'})
            result.setItem('unique',true,{'width':'5em','dtype':'B'})
            result.setItem('indexed',true,{'width':'5em','dtype':'B'})
            result.setItem('_relation',true,{'width':'20em',
                                            'editOnOpening':"var relation = rowData.getItem(field);genro.publish('edit_relation',{relation:relation?relation.deepCopy():null,rowIndex:rowIndex}); return false;"});
            this._columnsCellAttr = result;
        }
        return result;
    }
}

