# -*- coding: UTF-8 -*-

# colormenu.py
# Created by Francesco Porcari on 2017-01-08.
# Copyright (c) 2011 Softwell. All rights reserved.

"Test page description"
class GnrCustomWebPage(object):
    py_requires="gnrcomponents/testhandler:TestHandlerFull,gnrcomponents/framegrid:FrameGrid"
    def onMain_chromaImport(self):
        self.pageSource().dataController("genro.dom.loadJs('/_rsrc/js_libs/chroma.min.js',function(){});",_onStart=True)

    def windowTitle(self):
        return 'Colormenu'

         
    def test_0_filtering(self,pane):
        """First test description"""
        fb = pane.formbuilder(cols=2, border_spacing='4px')
        fb.callbackSelect(value='^.color',callback="""function(kw){
                var _id = kw._id;
                var _querystring = kw._querystring;
                var colorsDict = chroma.colors;
                var data = objectKeys(colorsDict).sort().map(function(n){
                    return {name:n,_pkey:colorsDict[n],color:'<div style="background:'+colorsDict[n]+';">&nbsp;&nbsp;<div>',caption:n}
                });
                var cbfilter = function(n){return true};
                if(_querystring){
                    _querystring = _querystring.slice(0,-1).toLowerCase();
                    cbfilter = function(n){return n.name.toLowerCase().indexOf(_querystring)>=0;};
                }else if(_id){
                    console.log('_id',n)
                    cbfilter = function(n){return n._pkey==_id;}
                }
                data = data.filter(cbfilter);
                return {headers:'name:Color,color:Sample',data:data}
            }""",auxColumns='name,color',lbl='Color Select',hasDownArrow=True,color='^.foreground',
            background='^.background_color')
        fb.dataController("""
                SET .background_color = bg;
                SET .foreground = chroma.contrast(bg,"white")>chroma.contrast(bg,"#444")?"white":"#444";
            """,
                bg='^.color',
                _if="window.chroma")

    def test_1_scales(self,pane):
        fb = pane.formbuilder(cols=1, border_spacing='4px')
        fb.textbox(value='^.colors',lbl='Colors')
        fb.numberTextBox(value='^.ns',lbl='Number of shades',default_value=5)
        fb.div("^.shades",lbl='Palette')
        fb.dataController("""
            var s = chroma.scale(_colors.split(',')).colors(_ns);
            var l = s.map(function(n){
                return '<div style="display:inline-block;width:30px;background:'+n+';">&nbsp;</div>';
            });
            SET .shades = l.join('');
            """,_ns='^.ns',_colors='^.colors')

        

    def test_2_menu(self,pane):
        """First test description"""
        fb = pane.formbuilder(cols=2, border_spacing='4px')
        fb.textbox(value='^.colors',lbl='Colors',default_value='white,black,blue,green,yellow,red,indigo')
        fb.numberTextBox(value='^.ns',lbl='Number of shades',default_value=20)
        fb.dataController("""
                        var b = new gnr.GnrBag();
                        var s = chroma.scale(_colors.split(',')).colors(_ns);
                        var l = s.forEach(function(n,idx){
                            var foreground = chroma.contrast(n,"white")>chroma.contrast(n,"#444")?"white":"#444";
                            var caption = '<div style="width:100%;text-align:center;background:'+n+';"><div style="display:inline-block;font-family:courier;color:'+foreground+'">'+n+'</div></div>';
                            b.setItem('r_'+idx,null,{caption:caption,color:n});
                        });
                        SET .hcolors = b;
                        """,
                        _onStart=True,_ns='^.ns',_colors='^.colors',_if='window.chroma')
        fb.textbox(value='^.color').comboMenu(storepath='.hcolors',
                                            _class='menupane',selected_color='.color')


    def test_3_colorTextBox(self,pane):
        fb = pane.formbuilder(cols=1, border_spacing='4px')
        fb.textbox(value='^.colors',lbl='Colors',default_value='white,black,blue,green,yellow,red,indigo')
        fb.numberTextBox(value='^.steps',lbl='Number of shades',default_value=20)
        fb.filteringSelect(value='^.mode',values='hex,rgba',lbl='Mode',default_value='hex')
        fb.colorTextBox(value='^.color',colors='^.colors',steps='^.steps',mode='^.mode',lbl='Color')

    def test_4_colorFiltering(self,pane):
        fb = pane.formbuilder(cols=1, border_spacing='4px')
        fb.colorFiltering(value='^.color',lbl='Color')


    def test_5_inGrid(self,pane):
        bc = pane.borderContainer(height='400px')
        g = bc.contentPane(region='center').quickGrid(value='^.colors')
        g.tools('delrow,addrow')
        g.column('filter_color',name='Filter Color',width='20em',edit=dict(tag='colorFiltering'))
        g.column('color_menu',name='Color Hex',width='20em',edit=dict(tag='colorTextBox'))
        g.column('color_hmenu',name='Color Rgba',width='20em',edit=dict(tag='colorTextBox',mode='rgba'))

