var page = {};
page.buildOnClient = function(){
    genro.src.getNode()._('div', '_test');
    var node = genro.src.getNode('_test').clearValue().freeze();
    alert('b');
    var dlg= node._('dialog',{nodeId:'_dlg_alert', title:'prova'});
    alert('c');
    var content = dlg._('div',{'height':'100px','width':'300px','background_color':'green'});
    content._('button',{label:'Pippo'});
    alert('c2');
    node.unfreeze();
    alert('d');
    genro.wdgById('_dlg_alert').show();
    alert('e');


};