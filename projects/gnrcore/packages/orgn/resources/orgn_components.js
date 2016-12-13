genro.orgn = {
    newQuickAnnotation:function(defaultkw){
        var frm = genro.formById('orgn_quick_annotation');
        defaultkw['rec_type'] = 'AN'
        frm.newrecord(defaultkw);
    }
}