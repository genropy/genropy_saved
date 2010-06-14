function formatLevel(value){
    var result = ''; //this is javascript callback you can put inside a separate module.
    value = parseInt(value);
    var colors = ['red','orange','yellow','darkgreen','green','lightgreen']
    for (var i=0; i<value ; i++){
        var style = "width:10px;height:14px;float:left;background:"+colors[i]+";";
        result = result+'<div style="'+style+'"> </div>';
    }
    return result;
}    
    