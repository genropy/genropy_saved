# -*- coding: UTF-8 -*-

# hello.py
# Created by Francesco Porcari on 2010-08-19.
# Copyright (c) 2010 Softwell. All rights reserved.

class GnrCustomWebPage(object):
    def main_root(self, root, **kwargs):
        root.button('do',showLabel=False,iconClass='icnBaseAdd',action="""
                                var red = genro.nodeById('RootNode');
                                
                                var green = genro.nodeById('RootNode/green_node');
                                //name = '^#RootNode/green_node.pluto';
                                
                                var blue = genro.nodeById('RootNode/green_node/blue_node');
                                
                                var blue2 = genro.nodeById('/blue_node',green);
                                
                                console.log(blue2,blue);
                                var blue3 = genro.nodeById('/green_node/blue_node',red);
                                
                                console.log(blue3,blue);
                                
                                var lime_1 = genro.nodeById('RootNode/green_node/blue_node/lime_node');
                                
                                var lime_2 = genro.nodeById('/green_node/blue_node/lime_node',red);
                                var lime_3 = blue.nodeById('/lime_node');

                                console.log('lime_node',lime_1,lime_2,lime_3);
                                """)
        red = root.div(height='200px',width='200px',background='red',childname='red_node',nodeId='RootNode')
        green = red.div(height='100px',width='100px',background='green',childname='green_node')
        blue = green.div(height='50px',width='50px',background='blue',childname='blue_node')
        foo = blue.div(height='30px',width='30px',background='white')
        foo.div(height='20px',width='20px',background='lime',childname='lime_node')