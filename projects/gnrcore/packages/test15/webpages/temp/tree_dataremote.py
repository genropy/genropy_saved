# -*- coding: UTF-8 -*-

# validate_password.py
# Created by Francesco Porcari on 2011-03-16.
# Copyright (c) 2011 Softwell. All rights reserved.

"Test page description"
class GnrCustomWebPage(object):
    py_requires="gnrcomponents/testhandler:TestHandlerFull"

        
    #def test_0_menu(self,pane):
    #    pane.dataRemote('.menu',self.relationExplorer,table='glbl.provincia',omit='_*',
    #                    x_resolved=True)
    #    pane.div(height='20px',width='20px',background='red',margin='20px').menu(storepath='.menu',modifiers='*')


    def test_1_tree(self,pane):
        pane.dataRemote('.tree',self.relationExplorer,table='glbl.provincia',omit='_*',
                        z_resolved=True)
        t =pane.div(height='20px',width='20px',background='green',margin='20px')
        t.menu(modifiers='*',onOpen="""
            console.log(this)
            var mbox = this.sourceNode.getValue().getItem('m_item.m_box');
            if(!mbox.getNode('m_tree')){
                mbox._('tree','m_tree',{storepath:'.tree'});
            }
            """).menuItem(childname='m_item').div(max_width='300px',height='200px',
                                                connect_onclick='console.log(e)',
                                                overflow='auto',childname='m_box')
        #m.tree(storepath='.tree')