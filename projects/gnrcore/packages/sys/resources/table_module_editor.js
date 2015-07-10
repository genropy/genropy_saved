var tableModuleEditor = {
    setCurrentStruct:function(sourceNode,checkedCols,allCols){
        var struct = new gnr.GnrBag();
        var cells = new gnr.GnrBag();
        var allCols = allCols?allCols.split(','):'name';
        struct.setItem('view_0.rows_0',cells);
        var checkedCols = checkedCols || 'name';
        var addedCols = [];
        cells.setItem('cell_name',null,{field:'name',edit:true,width:'10em',name:'name'});
        checkedCols.split(',').forEach(function(n){
            cells.setItem('cell_'+n,null,{field:n,edit:true,autoWdg:true,name:n,width:'10em'})
        });
        sourceNode.setRelativeData('#FORM.moduleColumnsStruct',struct);
    }
}