dojo.declare('gnr.ext.includedViewPicker', null, {
    constructor: function(sourceNode) {
        this.sourceNode = sourceNode;
    },
    addFromPicker: function(bagnode) {
        var assign;
        var result = {};
        var fields = this.sourceNode.attr.fromPicker_target_fields.split(',');
        for (var i = 0; i < fields.length; i++) {
            assign = stringStrip(fields[i]).split('=');
            result[assign[0].replace(/\W/g, '_')] = bagnode.attr[assign[1]];
        }
        ;
        return result;
    },

    fromPicker: function(nodelist) {
        var grid = this.sourceNode.widget;
        var nodupField = this.sourceNode.attr.fromPicker_nodup_field;
        grid.batchUpdating(true);
        grid.loadingContent(true);
        var defaultArgsList = [];
        for (var i = 0; i < nodelist.length; i++) {
            defaultArgsList.push(this.addFromPicker(nodelist[i]));
        }
        var lastPos;
        var newnodes = grid.newBagRow(defaultArgsList);

        for (var i = 0; i < newnodes.length; i++) {
            var node = newnodes[i];
            node.getValue();
            lastPos = grid.addBagRow(null, null, newnodes[i], null, nodupField);
        }
        grid.batchUpdating(false);
        grid.filterToRebuild(true);
        grid.updateRowCount('*');
        grid.selection.select(lastPos);
        grid.loadingContent(false);
    }
})
