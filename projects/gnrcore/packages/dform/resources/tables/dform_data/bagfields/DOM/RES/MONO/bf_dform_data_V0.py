from gnr.web.gnrbaseclasses import BagFieldForm

class BagField_values(BagFieldForm):
    def bf_content(self,pane,**kwargs):
        fb = pane.formbuilder()
        fb.textbox(value='^.val_1',lbl='val1')
        fb.textbox(value='^.val_2',lbl='val2')


class BagField_options(BagFieldForm):
    def bf_content(self,pane,**kwargs):
        fb = pane.formbuilder()
        fb.textbox(value='^.opt_1',lbl='opt1')
        fb.textbox(value='^.opt_2',lbl='Gamma2')
