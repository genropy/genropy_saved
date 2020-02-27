from gnr.web.gnrbaseclasses import BagFieldForm

class BagField_gamma(BagFieldForm):
    def bf_content(self,pane,**kwargs):
        fb = pane.formbuilder()
        fb.textbox(value='^.gamma_1',lbl='Gamma1')
        fb.textbox(value='^.gamma_2',lbl='Gamma2')


class BagField_delta(BagFieldForm):
    def bf_content(self,pane,**kwargs):
        fb = pane.formbuilder()
        fb.textbox(value='^.delta_1',lbl='delta1')
        fb.textbox(value='^.delta_2',lbl='delta2')
