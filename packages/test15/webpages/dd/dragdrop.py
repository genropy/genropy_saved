# -*- coding: UTF-8 -*-

# dragdrop.py
# Created by Francesco Porcari on 2010-10-01.
# Copyright (c) 2010 Softwell. All rights reserved.

"""Test drag & drop"""

class GnrCustomWebPage(object):
    """This is an example of Drag and Drop to support dragging of a field from one div to another even or to
       another application.  You can also drag files.  HTML5 is used to implement this feature.
       For a dropbox we have 'dropTags' and 'dropTypes'. A drop tag can have multiple tags and support boolean operators.
       For example: foo AND bar; client AND good,payer; so the comma implies an OR and the AND is explicit.
       A drop_type specifies whether it is plain text, xml, a file etc.
       
       From a source widget we can set it to 'draggable=True'. We can also have 'dragTags', and if we do,
       we can omit 'draggable=True' as it is implicit.
       From a source widget we can also define 'drag_value='.  This can be a path for example: =ccc.nnn.kkk' or =hhh.kkk?.yyy'
       If a div (or textbox or any widget) has a data value, then the data value is used, The data value can be an observer,
       for example ='^mydata'. The data dragged can be overridden by 'drag_value='.
       You can also have 'drag_cb='. In this case you get a callback and you can put any value.
       The callback parameters are: sourceNode, so you have all the info to know how to build the value to return.
       
       DRAG                        DROP
       draggable=True              dropTags = 'foo AND Bar'
       dragTags='foo AND Bar'      dropTypes = 'text/plain', 'xml', 'Files'
                                   onDrop = "js"
                                   drop_ext = 'gif' or 'py' or 'bar' , etc
    """
    py_requires = """gnrcomponents/testhandler:TestHandlerFull"""
    
    def test_0_dropBoxes(self, pane):
        """Drop Boxes"""
        fb = pane.formbuilder()
        dropboxes = fb.div(onDrop="""console.log(dropInfo);
                                     for (var k in data){
                                         alert(k+' :'+data[k])
                                         }""",
                           lbl='Drop boxes text/plain', dropTypes='*')
                           
        dropboxes.div('no tags', width='100px', height='50px', margin='3px', background_color='whitesmoke',
                      float='left', dropTarget=True)
        dropboxes.div('only foo', width='100px', height='50px', margin='3px', background_color='#fcfca9',
                      float='left', dropTags='foo', dropTarget=True)
        dropboxes.div('only bar', width='100px', height='50px', margin='3px', background_color='#ffc2f5',
                      float='left', dropTags='bar', dropTarget=True)
        dropboxes.div('only foo AND bar', width='100px', height='50px', margin='3px', background_color='#a7cffb',
                      float='left', dropTags='foo AND bar', dropTarget=True)
                      
        dropboxes = fb.div(onDrop="""var result=[];
                                     result.push('dropped '+files.length+' files:');
                                     dojo.forEach(files,function(f){
                                     result.push('name:'+f.name+' - size:'+f.size+' type:'+f.type);
                                     })
                                     result=result.join(_lf);
                                     alert(result);
                                     """,
                           lbl='Drop boxes Files', dropTypes='Files')
                           
        dropboxes.div('all types', width='100px', height='50px', margin='3px', background_color='whithesmoke',
                      float='left', dropTarget=True)
        dropboxes.div('only py', width='100px', height='50px', margin='3px', background_color='#fcfca9',
                      float='left', drop_ext='py', dropTarget=True)
        dropboxes.div('only py or xml', width='100px', height='50px', margin='3px', background_color='#ffc2f5',
                      float='left', drop_ext='bar', dropTarget=True)
        dropboxes.div('only gif', width='100px', height='50px', margin='3px', background_color='#a7cffb',
                      float='left', drop_ext='gif', dropTarget=True)
                      
    def test_1_simple(self, pane):
        """Simple Drag"""
        fb = pane.formbuilder(cols=2, dragClass='draggedItem')
        fb.div('Drag Me', width='70px', height='30px', margin='3px',
               background_color='green', lbl='drag it', draggable='^.cb1')
        fb.checkbox(value='^.cb1', label='draggable')
        
        fb.data('.mydiv', 'aaaabbbbbccc')
        fb.textBox(value='^.name', lbl='my name', draggable='^.cb2')
        
        fb.checkbox(value='^.cb2', label='draggable')
        fb.textBox(value='^.name2', lbl='alwaysdraggable', draggable=True)
        fb.br()
        # Si può anche usare dragValue="^.valoreDaDraggare" oppure onDrag="... imposta il valore da draggare ..."
        #
        # Vedi tablehandler_core.py e tablehandler_list.py per qualche esempio
        #
        # onDrag può:
        # - restituire False, per abortire il drag & drop;
        # - ha i parametri dragValues, dragInfo, treeItem (l'ultimo ha senso solo se dragghi da un albero)
        # - dragValues è l'envelope ove si possono aggiungere altri dati
        # - 
        
        fb = pane.formbuilder(dragClass='draggedItem')
        fb.div('^.mydiv', lbl='my div', draggable=True)
        fb.div('drag foo', dragTags='foo', lbl='drag with foo', draggable=True)
        fb.div('drag bar', dragTags='bar', lbl='drag with bar', draggable=True)
        fb.div('drag foo,bar', dragTags='foo,bar', lbl='drag with foo,bar', draggable=True)
        
    def test_2_dropimg(self, pane):
        """Drag checking tags"""
        pane.data('.imgurl', 'https://developer.mozilla.org/skins/mozilla/Fox3/img/mdc-logo.png')
        pane.img(dropTypes='Files', drop_ext='png,jpg,gif',
                 onDrop="""alert('ss')""",
                 src='^.imgurl')
                 