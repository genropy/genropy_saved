# -*- coding: UTF-8 -*-

# tooltipDialog.py
# Created by Francesco Porcari on 2011-03-18.
# Copyright (c) 2011 Softwell. All rights reserved.

"tooltipDialog"

class GnrCustomWebPage(object):
    py_requires="gnrcomponents/testhandler:TestHandlerFull"
    dojo_source=True
    
    def windowTitle(self):
        return 'tooltipDialog'
         
    def test_1_base(self,pane):
        """tooltipPane"""
        fb = pane.formbuilder(cols=2)
        textbox = fb.textbox(value='^.val', lbl='Choose Value',position='relative')
        textbox.div(_class='iconbox magnifier',position='absolute',right='2px',top='0px').menu(modifiers='*', _class='smallmenu',storepath='.qtySelection')
        
        pane.dataRpc('.qtySelection', self.db.table('pfrc.product_stock_price').getPriceGrid,
                      stock_id='Zsb3ZvqdNAmBwcH6YFMHTg',
                      order_date=self.workdate,_onStart=True)