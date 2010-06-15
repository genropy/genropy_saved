function formatLevel(value){
    var result = ''; //this is javascript callback you can put inside a separate module.
    value = parseInt(value);
    var colors = ['#6352b6','#9552b6','#bc5491','#cd5c5c','#ef0d0e'] 
    for (var i=0; i<value ; i++){
        var style = "width:10px;height:14px;float:left;background:"+colors[i]+";";
        console.log(i)
        result = result+'<div style="'+style+'"> </div>';
    }
    return result;
}    
//#['#527cb6','red','orange','yellow','darkgreen','green','lightgreen']