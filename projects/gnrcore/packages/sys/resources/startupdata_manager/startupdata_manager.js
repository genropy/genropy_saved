var startupdata_manager = {
    startupPackageChecked: function(tree, dataNode) {
        var current_data =
            tree.sourceNode.getRelativeData(".db_template_source") || new gnr.GnrBag();
        current_data = current_data.deepCopy();
        var package = dataNode.attr.file_name;
        var is_checking_true = !dataNode.attr.checked;
        if (is_checking_true) {
            if (current_data.getNode(package)) {
                return false;
            } else {
                current_data.setItem(package, null, {
                    package: package,
                    filepath: dataNode.attr.abs_path
                });
            }
        } else {
            current_data.popNode(package);
        }
        tree.sourceNode.setRelativeData(".db_template_source", current_data);
    }
};
