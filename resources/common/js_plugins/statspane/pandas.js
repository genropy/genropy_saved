var pandas_commands_manager = {
    commandMenu:function(commandStore,basecommands,dfcommands){
        var datasets_index = {};
        var result = basecommands.deepCopy();
        if(!commandStore || commandStore.len()===0){
            return result;
        }
        var r;
        result.setItem('sep',null,{caption:'-'});
        commandStore.values().forEach(function(v){
            var dfname = v.getItem('dfname');
            if(!(dfname in datasets_index)){
                datasets_index[dfname] = true;
                r = dfcommands.deepCopy();
                r._nodes.forEach(function(n){
                    n.attr.default_kw.dfname = dfname;
                });
                result.setItem('r_'+result.len(),r,{caption:dfname});
            }
        });
        return result;
    }
};