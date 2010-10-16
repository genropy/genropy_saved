# -*- coding: UTF-8 -*-

# batch_handler.py
# Created by Francesco Porcari on 2010-10-01.
# Copyright (c) 2010 Softwell. All rights reserved.


"""Test drag & drop"""
class GnrCustomWebPage(object):
    """This is an example of Drag and Drop to support dragging of a field from one div to another even or to
        another application.  You can also drag files.  HTML5 is used to implement this feature.
        For a dropbox we have 'drop_tags'and 'drop_types'.  A drop tag can have multiple tags and support boolean operators.
        For example: foo AND bar; client AND good,payer;   so the comma implies an OR and the AND is explicit.
        A drop_type specifies whether it is plain text, xml, a file etc.
        
        From a source widget we can set it to 'draggable=True'. We can also have 'drag_tags', and if we do, we can omit
        'draggable=True' as it is implicit.
        From a source widget we can also define 'drag_value='.  This can be a path for example: =ccc.nnn.kkk' or =hhh.kkk?.yyy'
        If a div ( or textbox or any widget) has a data value, then the data value is used, The data value can be an observer,
        for example ='^mydata'.  The data dragged can be overridden by 'drag_value='.  You can also have 'drag_cb='.  In this
        case you get a callback and you can put any value.  The callback parameters are: sourceNode, so you have all the info
        to know how to build the value to return.
        
        DRAG                        DROP
        draggable=True              drop_tags = 'foo AND Bar'
        drag_tags='foo AND Bar      drop_types = 'text/plain', 'xml', 'Files'
                                    drop_action = "js"
                                    drop_ext = 'gif' or 'py' or 'bar' , etc
        
        
        """
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

        fb.div('drag foo',drag_tags='foo',lbl='drag with foo')
        fb.div('drag bar',drag_tags='bar',lbl='drag with bar')
        fb.div('drag foo,bar',drag_tags='foo,bar',lbl='drag with foo,bar')
    
    def test_3_dropimg(self,pane):
        """Drag checking tags"""
        pane.data('.imgurl','https://developer.mozilla.org/skins/mozilla/Fox3/img/mdc-logo.png')
        pane.img(drop_types='Files',drop_ext='png,jpg,gif',
                       drop_action="""alert('ss')""",
                       src='^.imgurl')

        
        

        
        
