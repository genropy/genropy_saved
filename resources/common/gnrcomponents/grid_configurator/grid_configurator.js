var grid_conf ={};

grid_conf.get_struct_to_edit = function(gridNode){
        var attr = gridNode.attr;
        var currentStruct = gridNode.getRelativeData(attr.structpath);
        var editStruct = new gnr.GnrBag();
        var k = 0;
        currentStruct.getItem('#0.#0').forEach(function(n){
        var row = new gnr.GnrBag(n.attr);
            row.setItem('order',k);
            editStruct.setItem('r_'+k,row);
            k++;
        });
        return editStruct;
};
grid_conf.from_struct_to_edit = function(gridNode,structbag){
    var attr = gridNode.attr;
    var newstruct = new gnr.GnrBag();
    var k = 0;
    structbag.forEach(function(n){
        var nodeAttr = {};
        n.getValue().forEach(function(j){nodeAttr[j.label] = j.getValue()});
        newstruct.setItem('cell_'+k,null,nodeAttr);
        k++;
    });
    gridNode.setRelativeData(attr.structpath+'.view_0.rows_0',newstruct);
};