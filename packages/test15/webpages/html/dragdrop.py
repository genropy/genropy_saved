# -*- coding: UTF-8 -*-

# batch_handler.py
# Created by Francesco Porcari on 2010-10-01.
# Copyright (c) 2010 Softwell. All rights reserved.


"""Test drag & drop"""
class GnrCustomWebPage(object):
    py_requires="""gnrcomponents/testhandler:TestHandlerFull"""
    def test_0_dropBoxes(self,pane):
        """Drop Boxes"""
        fb=pane.formbuilder(cols=1)
        dropboxes=fb.div(drop_action='console.log("ddd");alert(drop_data)',lbl='Drop boxes text/plain',drop_types='text/plain')
                            
        dropboxes.div('no tags',width='100px',height='50px',margin='3px',background_color='#c7ff9a',
                            float='left')
        dropboxes.div('only foo',width='100px',height='50px',margin='3px',background_color='#fcfca9',
                            float='left',drop_tags='foo')
        dropboxes.div('only bar',width='100px',height='50px',margin='3px',background_color='#ffc2f5',
                            float='left',drop_tags='bar')
        dropboxes.div('only foo AND bar',width='100px',height='50px',margin='3px',background_color='#a7cffb',
                            float='left',drop_tags='foo AND bar')
        
        dropboxes=fb.div(drop_action="""var result=[];
                                        result.push('dropped '+files.length+' files:');
                                        dojo.forEach(files,function(f){
                                        result.push('name:'+f.name+' - size:'+f.size+' type:'+f.type);
                                        })
                                        result=result.join(_lf);
                                        alert(result);
                                        """,
                                         lbl='Drop boxes Files',drop_types='Files')
                            
        dropboxes.div('all types',width='100px',height='50px',margin='3px',background_color='#c7ff9a',
                            float='left')
        dropboxes.div('only py',width='100px',height='50px',margin='3px',background_color='#fcfca9',
                            float='left',drop_ext='py')
        dropboxes.div('only py or xml',width='100px',height='50px',margin='3px',background_color='#ffc2f5',
                            float='left',drop_ext='bar')
        dropboxes.div('only gif',width='100px',height='50px',margin='3px',background_color='#a7cffb',
                            float='left',drop_ext='gif')
                            
    def test_1_simple(self,pane):
        """Simple Drag"""
        fb=pane.formbuilder(cols=1,drag_class='draggedItem') 
        fb.div('Drag Me',width='70px',height='30px',margin='3px',
                    background_color='green',lbl='drag it',draggable=True)
        fb.data('.mydiv','aaaabbbbbccc',draggable=True)
        fb.textBox(value='^.name',lbl='my name',draggable=True)
        fb.div('^.mydiv',lbl='my div',draggable=True)
                         
    def test_2_checktag(self,pane):
        """Drag checking tags"""
        l=pane.ul(drag_class='draggedItem')
        l.li('drag foo',drag_tags='foo')
        l.li('drag bar',drag_tags='bar')
        l.li('drag foo,bar',drag_tags='foo,bar')
        

        
        
