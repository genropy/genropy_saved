# -*- coding: UTF-8 -*-

# builder.py
# Created by Francesco Porcari on 2011-02-26.
# Copyright (c) 2011 Softwell. All rights reserved.

"""builder"""

class GnrCustomWebPage(object):
    user_polling=0
    auto_polling=0
    
    def windowTitle(self):
        return 'Builder'
        
    def main(self,pane,**kwargs):
        bc = pane.borderContainer(datapath='test')
        bc.dataController("""
            var root = genro.nodeById("build_root");
            var current = genro.src.getNode(currentPath);
            console.log('currentNode',current);
            var cb = funcCreate(js_toeval,'root,current',root);
            cb(root,current);
            FIRE .onbuilt;
        """,js_toeval='^.evaluate_js',currentPath='=.currentPath')
        
        left = bc.borderContainer(region='left',width='300px',splitter=True)
        left.contentPane(region='bottom',overflow='hidden',onEnter='FIRE .do_eval;').simpleTextArea(value='^.js_toeval',
                                                            height='20ex',width='100%',
                                                            lbl='JS to eval')
        left.dataController("""SET .history= history+js_toeval+_lf;
                               FIRE .evaluate_js = js_toeval;
                               SET .js_toeval = '';
                            """,js_toeval="=.js_toeval",history='=.history',_fired='^.do_eval')
        fbleft = left.contentPane(region='top').formbuilder(cols=1, border_spacing='5px')
        fbleft.div('^.currentPath',lbl='currentNode',lbl_font_weight='bold')
        left.contentPane(region='center',overflow='hidden').simpleTextArea(value='^.history',width='100%',height='100%')
        right = bc.contentPane(region='right',width='300px',splitter=True)
        right.tree(storepath='#test_center.*S',_fired='^.onbuilt',
                    selectedPath='^.currentPath',
                    selectedLabelClass='selectedTreeNode')
        center = bc.contentPane(region='center',nodeId='test_center')
        center.contentPane(nodeId='build_root',margin='5px')
        