# -*- coding: utf-8 -*-

# validate_password.py
# Created by Francesco Porcari on 2011-03-16.
# Copyright (c) 2011 Softwell. All rights reserved.

"Test page description"
class GnrCustomWebPage(object):
    py_requires="gnrcomponents/testhandler:TestHandlerFull"

        
    def test_0_tree(self,pane):
        pane.dataRemote('.menu',self.relationExplorer,table='glbl.provincia',omit='_*',
                        z_resolved=True)
        pane.data('.caption','pippo')
        pane.div('^.caption',min_height='20px',min_width='60px',background='silver'
                ).tree(storepath='.menu',popup=True,
                        selected_caption='.caption')

    def test_10_tree(self,pane):
        pane.dataRemote('.menu',self.relationExplorer,table='glbl.provincia',omit='_*',
                        _resolved=True)
        pane.data('.caption','pippo')
        pane.div(min_height='20px',min_width='60px',background='silver'
                ).tree(storepath='.menu',popup=True)


    def test_1_tree(self,pane):
        pane.dataRemote('.tree',self.relationExplorer,table='glbl.provincia',omit='_*',
                        z_resolved=True)
    
        pane.div(height='20px',width='20px',
                    background='green',margin='20px'
                    ).tree(storepath='.tree',popup=dict(closeEvent='onClick',searchOn=True))

    def test_2_tree_checkbox(self,pane):
        pane.dataRemote('.tree',self.relationExplorer,table='glbl.provincia',omit='_*',
                        z_resolved=True)
    
        pane.div('^.checked',height='20px',width='200px',
                    margin='20px',border='1px solid silver'
                    ).tree(storepath='.tree',popup=True,
                            checked_caption='.checked',onChecked=True,_class='pippo')


    def test_3_doubletree(self,pane):
        pane.dataRemote('.tree',self.relationExplorer,table='glbl.provincia',omit='_*',
                        z_resolved=True)
    
        pane.div(height='20px',width='20px',
                    background='green',margin='20px'
                    ).tree(storepath='.tree',popup=True)

        pane.div(height='20px',width='20px',
                    background='red',margin='20px'
                    ).tree(storepath='.tree',popup=True,popup_close='click')


    def test_4_tree_and_menu(self,pane):
        pane.dataRemote('.tree',self.relationExplorer,table='glbl.provincia',omit='_*',
                        z_resolved=True)
    
        pane.div(height='20px',width='20px',
                    background='green',margin='20px'
                    ).tree(storepath='.tree',popup=True)

        pane.div(height='20px',width='20px',
                    background='red',margin='20px'
                    ).menu(storepath='.tree',modifiers='*')




