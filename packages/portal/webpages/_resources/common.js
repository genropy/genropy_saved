var staff = {};
staff.check_row = function(idx, evt, sourceNode, applyOn) {
    dojo.stopEvent(evt);
    var grid = sourceNode.widget;
    var storebag = grid.storebag();
    var bagNodes = storebag.getNodes();
    var row = bagNodes[idx];
    var attr = row.getAttr();
    attr['checked'] = !attr['checked'];
    row.setAttr(attr);
    this['align_' + applyOn](attr);
};

staff.align_tags = function(align_data) {
    var usertags = genro._('form.record.@user_id.auth_tags') || '';
    if (align_data['checked']) {
        var res = usertags ? usertags + ',' + align_data['tagname'] : align_data['tagname'];
        genro.setData('form.record.@user_id.auth_tags', res);
    }
    else {
        var tag_list = usertags.split(',');
        tag_list.splice(dojo.indexOf(tag_list, align_data['tagname']), 1);
        genro.setData('form.record.@user_id.auth_tags', tag_list.join(','));
    }
};
staff.align_roles = function(align_data) {
    var staffroles = genro._('form.record.roles');
    if (align_data['checked']) {
        var res = staffroles ? staffroles + ',' + align_data['description'] : align_data['description'];
        genro.setData('form.record.roles', res);
    }
    else {
        var role_list = staffroles.split(',');
        role_list.splice(dojo.indexOf(role_list, align_data['description']), 1);
        genro.setData('form.record.roles', role_list.join(','));
    }
};